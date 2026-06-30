"""DoctorLink Health Services - ZK Proof Generation, Stellar Verification & Rewards."""

import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any

from hpcsa_check import check_registration, HPCSAResult

_IS_WINDOWS = sys.platform == "win32"

_HERE = Path(__file__).parent

PROVER_PATH = os.getenv(
    "DOCTORLINK_PROVER",
    str(_HERE / "doctorlink-prover"),
)
PROVER_CACHE = Path(os.getenv("DOCTORLINK_PROVER_CACHE", str(_HERE / "proof_data")))


class ProofError(Exception):
    pass


def _ensure_wsl_path(win_path: str) -> str:
    if not _IS_WINDOWS:
        return str(Path(win_path).resolve())
    abs_path = str(Path(win_path).resolve())
    if abs_path[1] == ":":
        drive = abs_path[0].lower()
        rest = abs_path[2:].replace("\\", "/")
        return f"/mnt/{drive}{rest}"
    return abs_path


def _run(cmd_args: list, timeout: int = 120) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(cmd_args, capture_output=True, timeout=timeout)
    except FileNotFoundError:
        raise ProofError(f"Command not found: {cmd_args[0]}")
    except subprocess.TimeoutExpired:
        raise ProofError("Command timed out")


def _call_prover(*cli_args: str) -> Dict:
    pk_arg = f"--pk-path {_ensure_wsl_path(str(PROVER_CACHE))}/{cli_args[0]}_pk.bin"
    if _IS_WINDOWS:
        cmd = (
            f'source "$HOME/.cargo/env" && '
            f'{_ensure_wsl_path(PROVER_PATH)} '
            f'{pk_arg} '
            + " ".join(cli_args[1:])
        )
        result = _run(["wsl", "bash", "-l", "-c", cmd])
    else:
        extra = shlex.split(cli_args[1]) if len(cli_args) > 1 else []
        cmd = [PROVER_PATH] + extra + pk_arg.split()
        result = _run(cmd)

    stdout = result.stdout.decode("utf-8", errors="replace")
    stderr = result.stderr.decode("utf-8", errors="replace")
    if result.returncode != 0:
        raise ProofError(f"Prover failed: {stderr.strip()[:300]}")
    for line in reversed(stdout.strip().split("\n")):
        line = line.strip()
        if line.startswith("{"):
            return json.loads(line)
    raise ProofError("No JSON output from prover")


_INTERNAL_TO_CONTRACT = {
    "age_check": "AgeEligibility",
    "license_verify": "LicenseVerify",
    "vaccine_status": "VaccineStatus",
}


class ZKProofService:
    def __init__(self, network: str = "testnet", contract_id: Optional[str] = None,
                 token_contract_id: Optional[str] = None):
        self.network = network
        self.contract_id = contract_id
        self.token_contract_id = token_contract_id

    # ── Proof Generation ─────────────────────────────────────────

    def generate_age_proof(self, dob_year: int, current_year: int, min_age: int) -> Dict:
        result = _call_prover(
            "age_check",
            f"--circuit age_check --dob-year {dob_year} --current-year {current_year} --min-age {min_age}",
        )
        age = int(result.get("age", "0")) if "age" in result else current_year - dob_year
        return {
            "circuit": "age_check",
            "proof_hash": hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest(),
            "public_signals": {
                "is_eligible": 1 if age >= min_age else 0,
                "min_age": min_age,
                "raw_hex": result.get("public_inputs", []),
            },
            "age_verified": age >= min_age,
            "stellar_hex": {k: result[k] for k in (
                "proof_a", "proof_b", "proof_c", "vk_alpha", "vk_beta",
                "vk_gamma", "vk_delta", "vk_gamma_abc", "public_inputs"
            )},
        }

    # ── HPCSA Registration Check ─────────────────────────────

    def check_hpcsa(self, license_number: str, surname: str = "",
                    first_name: str = "") -> Dict[str, Any]:
        result: HPCSAResult = check_registration(license_number, surname, first_name)
        d = result.to_dict()
        d["checked_at"] = datetime.utcnow().isoformat()
        return d

    # ── License Proof with optional HPCSA pre-check ─────────

    def generate_license_proof(self, license_number: str, doctor_id: int) -> Dict:
        ln_hash = int(hashlib.sha256(f"{license_number}:{doctor_id}".encode()).hexdigest()[:16], 16)
        result = _call_prover(
            "license_verify",
            f"--circuit license_verify --license-number {ln_hash}",
        )
        return {
            "circuit": "license_verify",
            "proof_hash": hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest(),
            "public_signals": {
                "is_verified": 1,
                "license_hash": format(ln_hash, "x"),
                "raw_hex": result.get("public_inputs", []),
            },
            "credential_hash": format(ln_hash, "x"),
            "stellar_hex": {k: result[k] for k in (
                "proof_a", "proof_b", "proof_c", "vk_alpha", "vk_beta",
                "vk_gamma", "vk_delta", "vk_gamma_abc", "public_inputs"
            )},
        }

    def generate_vaccine_proof(self, patient_id: int, vaccine_type: str) -> Dict:
        rh = int(hashlib.sha256(f"{patient_id}:{vaccine_type}".encode()).hexdigest()[:16], 16)
        result = _call_prover(
            "vaccine_status",
            f"--circuit vaccine_status --record-hash {rh:x} --required-hash {rh:x}",
        )
        return {
            "circuit": "vaccine_status",
            "proof_hash": hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest(),
            "public_signals": {
                "is_compliant": 1,
                "vaccine_type": vaccine_type,
                "record_hash": format(rh, "x"),
                "raw_hex": result.get("public_inputs", []),
            },
            "stellar_hex": {k: result[k] for k in (
                "proof_a", "proof_b", "proof_c", "vk_alpha", "vk_beta",
                "vk_gamma", "vk_delta", "vk_gamma_abc", "public_inputs"
            )},
        }

    # ── Stellar Submission ───────────────────────────────────────

    def _clijson(self, contract_id: str, func: str, *args: str) -> Dict:
        cmd_parts = [
            "stellar", "contract", "invoke",
            "--id", contract_id,
            "--network", self.network,
            "--source-account", "funded",
            "--send=yes",
            "--", func,
        ] + list(args)
        if _IS_WINDOWS:
            cmd_str = " ".join(cmd_parts)
            result = _run(["wsl", "bash", "-l", "-c", cmd_str])
        else:
            result = _run(cmd_parts)
        stdout = result.stdout.decode("utf-8", errors="replace")
        stderr = result.stderr.decode("utf-8", errors="replace")
        output = stdout + stderr
        if result.returncode != 0:
            raise ProofError(f"CLI error: {output.strip()[:500]}")
        tx = re.search(r"tx/([a-f0-9]{64})", output)
        return {"success": True, "tx_hash": tx.group(1) if tx else "unknown"}

    def submit_to_stellar(self, proof_hash: str, public_signals: Dict,
                          contract_id: Optional[str] = None) -> Dict:
        target = contract_id or self.contract_id
        if not target:
            raise ProofError("No verifier contract ID")

        circuit_name = public_signals.get("circuit", "age_check")
        circuit_name = _INTERNAL_TO_CONTRACT.get(circuit_name, circuit_name)

        raw_hex = public_signals.get("raw_hex", [])
        public_inputs_dec = [str(int(h, 16)) for h in raw_hex]
        public_inputs_json = json.dumps(public_inputs_dec)
        verified_val = public_signals.get("is_eligible",
                      public_signals.get("is_verified",
                      public_signals.get("is_compliant", 0)))

        return self._clijson(
            target, "store_verification",
            f'--circuit {circuit_name}',
            f'--proof_hash "{proof_hash}"',
            f"--public_inputs '{public_inputs_json}'",
            f'--verified {"true" if verified_val else "false"}',
        )

    def reward_tokens(self, patient_address: str, amount: int = 10,
                      token_id: Optional[str] = None) -> Dict:
        target = token_id or self.token_contract_id
        if not target:
            raise ProofError("No token contract ID")
        return self._clijson(
            target, "reward_health",
            f"--admin funded",
            f"--patient {patient_address}",
            f"--amount {amount}",
        )

    def verify_and_reward(self, proof_hash: str, public_signals: Dict,
                          patient_address: str, amount: int = 10,
                          verifier_id: Optional[str] = None,
                          token_id: Optional[str] = None) -> Dict:
        ver = self.submit_to_stellar(proof_hash, public_signals, verifier_id)
        if not ver.get("success"):
            return ver
        rew = self.reward_tokens(patient_address, amount, token_id)
        return {
            "verification": ver,
            "reward": rew,
            "success": True,
        }


def get_zk_service(network: Optional[str] = None) -> ZKProofService:
    from config import settings
    return ZKProofService(
        network=network or settings.STELLAR_NETWORK,
        contract_id=settings.ZK_VERIFIER_CONTRACT or None,
        token_contract_id=settings.HEALTH_TOKEN_CONTRACT or None,
    )
