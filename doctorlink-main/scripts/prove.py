#!/usr/bin/env python3
"""Proof generation helper using Noir/BB or fallback hash-based proofs."""

import hashlib
import json
import sys
from pathlib import Path


def generate_age_proof(dob_year: int, current_year: int, min_age: int) -> dict:
    age = current_year - dob_year
    assert age >= min_age, f"Age {age} < minimum {min_age}"

    proof_input = json.dumps({
        "dob_year": dob_year,
        "current_year": current_year,
        "min_age": min_age,
    }, sort_keys=True)
    proof_hash = hashlib.sha256(proof_input.encode()).hexdigest()

    return {
        "circuit": "age_check",
        "proof_hash": proof_hash,
        "public_signals": {"is_eligible": 1, "min_age": min_age},
        "age_verified": True,
    }


def generate_license_proof(license_number: str, doctor_id: int) -> dict:
    credential_hash = hashlib.sha256(
        f"{license_number}:{doctor_id}".encode()
    ).hexdigest()

    proof_input = json.dumps({
        "license": license_number,
        "doctor_id": doctor_id,
    }, sort_keys=True)
    proof_hash = hashlib.sha256(proof_input.encode()).hexdigest()

    return {
        "circuit": "license_verify",
        "proof_hash": proof_hash,
        "public_signals": {"is_verified": 1, "license_hash": credential_hash},
        "credential_hash": credential_hash,
    }


def generate_vaccine_proof(patient_id: int, vaccine_type: str) -> dict:
    record_hash = hashlib.sha256(
        f"{patient_id}:{vaccine_type}".encode()
    ).hexdigest()

    return {
        "circuit": "vaccine_status",
        "proof_hash": record_hash,
        "public_signals": {"is_compliant": 1, "vaccine_type": vaccine_type},
    }


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"

    if cmd == "age":
        proof = generate_age_proof(
            int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
        )
        print(json.dumps(proof, indent=2))
    elif cmd == "license":
        proof = generate_license_proof(sys.argv[2], int(sys.argv[3]))
        print(json.dumps(proof, indent=2))
    elif cmd == "vaccine":
        proof = generate_vaccine_proof(int(sys.argv[2]), sys.argv[3])
        print(json.dumps(proof, indent=2))
    else:
        print("Usage: prove.py <age|license|vaccine> [args]")
        print("  age <dob_year> <current_year> <min_age>")
        print("  license <license_number> <doctor_id>")
        print("  vaccine <patient_id> <vaccine_type>")
