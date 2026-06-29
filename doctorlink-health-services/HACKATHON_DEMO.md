# DoctorLink ZK Health Compliance — Hackathon Demo

## Problem
Remote mobile clinics in rural areas need to verify patient eligibility (age ≥ 18, valid medical license, vaccine compliance) **without internet access** and without exposing sensitive personal data like DOB or license numbers. On-chain records must be immutable and auditable.

## Solution
**Zero-Knowledge Proofs + Stellar Soroban** — generate Groth16 proofs offline, anchor verification records on Stellar testnet when connectivity is available, and reward patients with DLHT tokens.

---

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────────┐
│  FastHTML   │────▶│  Python API  │────▶│  Rust Prover     │
│  Frontend   │     │  (FastAPI)   │     │  (arkworks BN254)│
│  :8001      │     │  :8000       │     │  │               │
└─────────────┘     └──────┬───────┘     └────────┬─────────┘
                           │                      │
                           ▼                      ▼
                    ┌──────────────┐     ┌──────────────────┐
                    │ SQLite DB    │     │ Groth16 Proof    │
                    │ (patients,   │     │ (R1CS → BN254)   │
                    │  queue)      │     └────────┬─────────┘
                    └──────────────┘              │
                                                  ▼
                                          ┌──────────────────┐
                                          │ Stellar Testnet   │
                                          │ ┌──────────────┐  │
                                          │ │ Verifier     │  │
                                          │ │ Contract     │  │
                                          │ └──────────────┘  │
                                          │ ┌──────────────┐  │
                                          │ │ Token        │  │
                                          │ │ Contract     │  │
                                          │ └──────────────┘  │
                                          └──────────────────┘
```

---

## Components

### 1. ZK Circuits (`doctorlink-main/circuits/`)
- **AgeEligibility**: Proves age ≥ min_age without revealing DOB
- **LicenseVerify**: Proves doctor holds a valid license hash
- **VaccineStatus**: Proves vaccination record matches requirement

### 2. Rust Prover (`doctorlink-main/prover/`)
- arkworks-based Groth16 prover targeting BN254 curve
- Proving keys cached per circuit
- CLI: `--circuit age_check|license_verify|vaccine_status`
- Outputs JSON with hex-encoded proof points + VK

### 3. Soroban Contracts (`doctorlink-main/contracts/`)
- **doctorlink-verifier**: `store_verification`, `get_last_verification`, `verify_groth16`
- **doctorlink-token**: `initialize`, `transfer`, `reward_health` (DLHT)

### 4. Python Backend (`doctorlink-health-services/`)
- FastAPI endpoints: patients, doctors, verifications, sync
- FastHTML frontend at `:8001`: dashboard, patients, queue, on-chain viewer
- `zk_service.py`: orchestrates prover + Stellar submission + token rewards
- `hpcsa_check.py`: **HPCSA iRegister integration** — validates doctor license numbers against the SA Health Professions Council's online register before generating ZK proofs

---

## HPCSA iRegister Integration

DoctorLink queries the [HPCSA iRegister](https://hpcsaonline.custhelp.com/app/i_reg_form) as a **pre-proving credential check**:

```
Doctor License # → HPCSA iRegister → Active? → Generate ZK Proof → Stellar
```

- **Live mode**: POST to `/cc/ReportController/getDataFromRnow` (requires Oracle RightNow session cookie)
- **Mock fallback**: Returns realistic data for known demo numbers; "Not Found" for fake license numbers
- **SA doctors**: Use HPCSA-format registration numbers (`MP0456789`, `MP0987654`) — mock returns "Active"
- **International/fake**: Numbers like `LIC-98765-MD` return "Not Found" with explanatory message

The mock layer demonstrates how real HPCSA validation would gate the ZK proof pipeline. In production:
1. HPCSA would provide an official API or partnership
2. A headless browser (Playwright) could drive the existing web form
3. Only HPCSA-verified doctors would proceed to ZK proof generation

---

## Demo Walkthrough

### Prerequisites
```bash
# Start the frontend
cd doctorlink-health-services
$env:STELLAR_SECRET_KEY="SCNUOMFLGHCNSDQLTS7J25OAOP7ME764XH23ZBXM4TXZRJT3SLQAADA6"
python -c "import uvicorn; uvicorn.run('frontend:app', host='0.0.0.0', port=8001)"
```

### Step 1: Dashboard
Open `http://localhost:8001/`
- Shows Remote Clinic and Telehealth mode cards
- Navigate to Patients

### Step 2: Generate ZK Proof
Click **Verify Age** on any patient
- Backend calls Rust prover with patient's DOB year
- Groth16 proof generated and verified locally
- Proof stored on Stellar testnet

### Step 3: View On-Chain State
Navigate to **On-Chain** tab
- See stored `VerificationRecord`
- Check DLHT token balance

### Step 4: Reward Tokens
Click **Reward** on a patient
- Admin calls `reward_health` on token contract
- Patient receives DLHT tokens as compliance reward

### Step 5: Offline Queue
Navigate to **Queue** tab
- See pending sync items from offline verifications
- Click **Sync All** to submit pending proofs

### Step 6: HPCSA License Check (South Africa)
From the Patients page, click **HPCSA** next to any doctor
- SA doctors (`MP0456789` Thabo Mokoena, `MP0987654` Lindiwe Nkosi) return "Active"
- International/fake numbers (`LIC-...`) return "Not Found"
- The HPCSA check runs before ZK proof generation — only active registrations proceed

---

## Contract Addresses (Testnet)

| Contract | ID | Explorer |
|----------|----|----------|
| Verifier | `CAB7ZADYO7M7NWYBNCMLTLO4SCQTHGHMW5QBMWJBOSA5HKMOUFTN6AN2` | [View](https://stellar.expert/explorer/testnet/contract/CAB7ZADYO7M7NWYBNCMLTLO4SCQTHGHMW5QBMWJBOSA5HKMOUFTN6AN2) |
| Token (DLHT) | `CBZ5ZNC6I4NOWKGFJOECMYJWUQ2QGQZ622PJQIV6EK427WVS3HONQGRT` | [View](https://stellar.expert/explorer/testnet/contract/CBZ5ZNC6I4NOWKGFJOECMYJWUQ2QGQZ622PJQIV6EK427WVS3HONQGRT) |

## Account (Fee Sponsor)

| Identity | Address |
|----------|---------|
| funded | `GCLJMFKL3CFWJKZS6UM5BF5KWG67UMVL7TCSDAM4L3JIFWNMV3LSIFL7` |

---

## Example Transaction Hashes

| Action | Tx Hash |
|--------|---------|
| store_verification (age≥18) | `b5c0b9117827242a302f6489d61cf8d6b55eb321b8af1e3607dd7737952002db` |
| reward_health (10 DLHT) | `cb704ba8d99a5f5176525e4f2113bd6ea37de28dcda0e3a40919baadbf3d4c2c` |

---

## File Structure

```
doctorlink-main/
├── circuits/src/          # Noir ZK circuits
├── contracts/              # Soroban contracts
│   ├── doctorlink-verifier/
│   └── doctorlink-token/
├── prover/src/main.rs     # Rust Groth16 prover
├── proof_data/            # Cached proving keys + proofs
└── scripts/               # Deploy + test scripts

doctorlink-health-services/
├── api/v1/endpoints.py    # FastAPI REST endpoints
├── frontend.py            # FastHTML frontend
├── zk_service.py          # Proof generation + Stellar
├── hpcsa_check.py         # HPCSA iRegister validation
├── models.py              # SQLAlchemy models
├── config.py              # Settings
└── .env                   # Secrets (gitignored)
```
