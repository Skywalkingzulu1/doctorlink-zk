# DoctorLink — ZK Health Compliance on Stellar

> **Built for Stellar Hacks: Real-World ZK · June 2026**
> Monorepo: Noir circuits + arkworks Groth16 prover + Soroban contracts + Python frontend

## The Problem

Remote mobile clinics in rural South Africa need to verify patient eligibility (age ≥ 18, vaccine compliance, valid doctor licenses) **without internet** and **without exposing sensitive personal data**. Current approaches either transmit health data over unreliable networks (privacy risk) or stop working when offline.

## The Solution

Three Noir ZK circuits generate Groth16 proofs on-device (offline-capable). The proof hash is anchored on Stellar Soroban for an immutable audit trail. Patients earn DLHT tokens as compliance rewards.

### What ZK enables

| Verification | Proves | Without revealing |
|---|---|---|
| **Age ≥ 18** | `birth_year ≤ current_year - 18` | Exact date of birth |
| **Vaccine status** | `vaccine_name matches requirement` | Full medical history |
| **License valid** | `license_hash in merkle_tree` | License number |

## Repository Structure

```
doctorlink-main/
├── circuits/                  # 3 Noir ZK circuits (BN254)
│   └── src/
│       ├── age_check.nr       # Prove age ≥ 18 without DOB
│       ├── license_verify.nr  # Prove valid doctor license
│       └── vaccine_status.nr  # Prove vaccine compliance
├── contracts/
│   ├── doctorlink-verifier/   # Soroban Groth16 verifier (BN254)
│   └── doctorlink-token/      # DLHT reward token
├── prover/                    # Rust arkworks Groth16 prover
│   └── src/main.rs            # CLI: --circuit <name>
├── proof_data/                # Cached proving keys + proofs
├── scripts/                   # Deploy + test scripts
└── doctorlink-health-services/ # Python frontend + API
    ├── frontend.py            # FastHTML dashboard (dark glassmorphism)
    ├── zk_service.py          # ZK orchestration + Stellar
    ├── ai_service.py          # OpenRouter AI (Gemini 2.5 Flash Lite)
    ├── clinic_service.py      # Octoparse clinic API + 20 SA clinics
    ├── hpcsa_check.py         # HPCSA iRegister validation
    └── README.md              # Full project README with demo walkthrough
```

## Smart Contracts (Deployed on Stellar Testnet)

### Verifier — `CAB7ZADYO7M7NWYBNCMLTLO4SCQTHGHMW5QBMWJBOSA5HKMOUFTN6AN2`
- `verify_groth16(vk, proof, public_inputs)` — Verify BN254 Groth16 proof
- `store_verification(circuit, proof_hash, public_inputs, verified)` — Anchor proof on-chain

### Token (DLHT) — `CBZ5ZNC6I4NOWKGFJOECMYJWUQ2QGQZ622PJQIV6EK427WVS3HONQGRT`
- `initialize(admin, name, symbol)` — Set up reward token
- `reward_health(admin, patient, amount)` — Mint rewards for compliance
- `balance(id)` — Check token balance

## ZK Pipeline

```
┌─────────┐    ┌──────────┐    ┌────────────┐    ┌────────────────┐
│ Noir     │───▶│ Rust     │───▶│ Soroban    │───▶│ Stellar        │
│ Circuit  │    │ Prover   │    │ Verifier   │    │ Testnet        │
│ (.nr)    │    │ (arkworks│    │ Contract   │    │ (immutable)    │
└─────────┘    │ BN254)   │    └────────────┘    └────────────────┘
               └──────────┘
```

Circuits are compiled with Noir 1.0.0-beta.22. The Rust prover uses arkworks 0.4 on the BN254 curve, generating Groth16 proofs with LibsnarkReduction. Proving keys are cached for reuse.

## HPCSA Integration (South Africa)

DoctorLink validates doctor registration numbers against the **HPCSA iRegister** before generating ZK license proofs — ensuring only actively registered SA practitioners get verified. Mock fallback for demo.

## Quick Start

```bash
# Backend + frontend
cd doctorlink-health-services
pip install -r requirements.txt
cp .env.example .env  # add your keys
python -c "import uvicorn; uvicorn.run('frontend:app', host='0.0.0.0', port=8001)"
# Open http://localhost:8001
```

## See Also

- `doctorlink-health-services/README.md` — Full project README with demo walkthrough
- `doctorlink-health-services/HACKATHON_DEMO.md` — Expanded demo guide
