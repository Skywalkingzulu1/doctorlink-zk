# DoctorLink — Private Health Compliance for Remote Mobile Clinics

> **Built for Stellar Hacks: Real-World ZK · June 2026**
> Deadline: June 29, 2026

## The Problem

**5 million South Africans rely on mobile clinics** in rural areas where internet connectivity is unreliable or non-existent. These clinics need to:

- Verify a patient is **over 18** for contraceptive programs
- Confirm **vaccination records** match requirements
- Check that a **doctor's license** is valid

Current approaches expose sensitive personal data (DOB, vaccine records, license numbers) over unreliable networks — a privacy risk. And when there's no internet, verification simply stops.

## The Solution

**DoctorLink** generates zero-knowledge proofs **offline** on a local device. The clinic proves compliance without transmitting private data. Proofs are cached locally and anchored on **Stellar Soroban** when connectivity returns. Patients earn **DLHT tokens** as rewards.

```
Patient data → ZK Circuit → Groth16 Proof (offline) → Stellar Testnet (online)
     🔒 stays here       🔐 proof only        ⛓️ immutable record
```

### What ZK proves, and what stays private

| Verification | Proves | Without revealing |
|---|---|---|
| **Age ≥ 18** | `birth_year ≤ current_year - 18` | Exact DOB |
| **Vaccine status** | `vaccine_name == "COVID-19"` | Full medical history |
| **License valid** | `license_hash in merkle_tree` | License number |

ZK is **load-bearing** here — without it, the clinic would have to transmit raw health data to prove compliance. With it, only a cryptographic proof leaves the device.

## Why Stellar

Stellar's recent Protocol 25 and 26 introduced **native BN254 host functions** — elliptic-curve operations, multi-scalar multiplication, and Poseidon hashing — making on-chain Groth16 verification affordable. We deploy:

1. **doctorlink-verifier** — stores verification records (`store_verification`, `get_last_verification`)
2. **doctorlink-token** — DLHT reward token (`reward_health`, `balance`)

Both deployed on **Stellar Testnet** and fully functional.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  FastHTML UI     │────▶│  zk_service.py   │────▶│  Rust Prover      │
│  (dark glass)    │     │  (orchestrator)  │     │  (arkworks BN254  │
│  :8001           │     │  :8000           │     │   Groth16)        │
└─────────────────┘     └────────┬─────────┘     └────────┬─────────┘
                                 │                        │
                          ┌──────▼──────┐          ┌──────▼──────┐
                          │ SQLite DB    │          │ Groth16     │
                          │ (patients,   │          │ Proof       │
                          │  doctors,    │          │ + VK        │
                          │  queue)      │          └──────┬──────┘
                          └──────┬──────┘                 │
                                 │                         │
                          ┌──────▼─────────────────────────▼──────┐
                          │           Stellar Testnet              │
                          │  ┌─────────────────┐  ┌────────────┐   │
                          │  │ Verifier Contract│  │ Token (DLHT)│   │
                          │  │ CAB7ZADY...      │  │ CBZ5ZNC...  │   │
                          │  └─────────────────┘  └────────────┘   │
                          └────────────────────────────────────────┘
```

## What We Built

### 3 Noir ZK Circuits (`doctorlink-main/circuits/`)
- **AgeEligibility** — proves `age ≥ min_age` without DOB
- **LicenseVerify** — proves doctor holds a valid license
- **VaccineStatus** — proves vaccine matches requirement

### Rust Prover (`doctorlink-main/prover/`)
- Arkworks-based Groth16 on **BN254** (matching Noir's Barretenberg backend)
- Proving keys cached per circuit
- Generates real Groth16 proofs via CLI

### 2 Soroban Contracts (deployed on testnet)
- **Verifier**: `CAB7ZADYO7M7NWYBNCMLTLO4SCQTHGHMW5QBMWJBOSA5HKMOUFTN6AN2`
- **Token (DLHT)**: `CBZ5ZNC6I4NOWKGFJOECMYJWUQ2QGQZ622PJQIV6EK427WVS3HONQGRT`

### FastHTML Frontend with Dark Glassmorphism UI
- Dashboard with problem-first narrative and step-by-step flow
- Patient/doctor directory with ZK verification actions
- On-chain viewer pulling live data from Stellar testnet
- Sync queue for offline-generated proofs
- HPCSA iRegister integration for SA doctor license validation
- AI-powered clinic finder, triage, and chat (OpenRouter / Gemini 2.5 Flash Lite)

### AI Assistant (Dr. Link)
- **Clinic Finder** — searches SA clinic directory (20+ clinics seeded from Netcare, Mediclinic, Life Healthcare, Government, Private)
- **Symptom Triage** — step-by-step assessment with care recommendations
- **General Chat** — answers questions about DoctorLink, ZK, and health topics
- All powered by **Gemini 2.5 Flash Lite** via OpenRouter

### HPCSA Validation (South Africa)
DoctorLink validates doctor registration numbers against the **HPCSA iRegister** (Health Professions Council of South Africa) before generating ZK license proofs. SA-format numbers (`MP0456789`, `PS123456`, `DN0456789`) return active registration status; fake/international numbers return "Not Found".

### Offline-First Architecture
1. Generate ZK proof locally in the field (no internet required)
2. Cache proof hash + public signals in `stellar_sync_queue`
3. When connectivity returns, batch-sync to Stellar Soroban
4. View anchored records on the On-Chain page

## Demo Walkthrough

### Prerequisites
```bash
cd doctorlink-health-services
pip install -r requirements.txt
cp .env.example .env  # add your keys
python -c "import uvicorn; uvicorn.run('frontend:app', host='0.0.0.0', port=8001)"
```

### Step 1: Open the Dashboard
`http://localhost:8001/` — see the problem narrative and 3-step how-it-works flow.

### Step 2: Verify a Patient
Go to **Patients** → click **Age** on any patient → a Groth16 proof is generated on-device and submitted to Stellar. The result card shows the proof hash and a link to Stellar Explorer.

### Step 3: Check On-Chain
Go to **On-Chain** — see the last verification record and the DLHT token balance pulled live from Stellar testnet.

### Step 4: Reward Tokens
Go to **Patients** → click **Reward** → the patient receives DLHT tokens as a compliance incentive.

### Step 5: Sync Queue
Go to **Queue** → view pending proofs → click **Sync All** to batch-submit to Stellar.

### Step 6: AI Tools
Go to **Clinic Finder** → search by location or ask Dr. Link for a recommendation. Try **Triage** for symptom assessment.

## Contract Addresses (Testnet)

| Contract | Address |
|---|---|
| Verifier | `CAB7ZADYO7M7NWYBNCMLTLO4SCQTHGHMW5QBMWJBOSA5HKMOUFTN6AN2` |
| Token (DLHT) | `CBZ5ZNC6I4NOWKGFJOECMYJWUQ2QGQZ622PJQIV6EK427WVS3HONQGRT` |
| Fee Sponsor | `GCLJMFKL3CFWJKZS6UM5BF5KWG67UMVL7TCSDAM4L3JIFWNMV3LSIFL7` |

## Tech Stack

| Layer | Technology |
|---|---|
| Circuit | Noir 1.0.0-beta.22 |
| Prover | Rust / arkworks 0.4 (BN254 Groth16) |
| Blockchain | Stellar Soroban (testnet) |
| Backend | Python / FastHTML |
| Frontend | FastHTML + Tailwind + custom CSS |
| AI | OpenRouter / Google Gemini 2.5 Flash Lite |
| Clinic Data | Octoparse REST API + 20 seeded SA clinics |
| License Check | HPCSA iRegister (live POST + mock fallback) |

## Repository Structure

```
doctorlink-main/              # Monorepo root
├── circuits/src/              # 3 Noir ZK circuits
├── contracts/                 # Soroban contracts
│   ├── doctorlink-verifier/
│   └── doctorlink-token/
├── prover/src/main.rs         # Rust Groth16 prover
├── proof_data/                # Cached proving keys
└── scripts/                   # Deploy + helper scripts

doctorlink-health-services/    # Application
├── frontend.py                # FastHTML frontend (all routes)
├── zk_service.py              # ZK orchestration + Stellar
├── ai_service.py              # OpenRouter AI client
├── clinic_service.py          # Octoparse clinic API + seed data
├── hpcsa_check.py             # HPCSA iRegister validation
├── models.py                  # SQLAlchemy models
├── config.py                  # Settings
├── .env                       # Secrets (gitignored)
├── README.md                  # ← You are here
└── HACKATHON_DEMO.md          # Expanded demo walkthrough
```

## Notes

- **BN254 curve**: Chosen to match Noir's Barretenberg backend (not BLS12-381)
- **Mock data**: 5 patients and 4 doctors are pre-seeded for demo; all are clearly labeled as sample/test data
- **HPCSA live check**: Times out due to Oracle RightNow JS requirements; mock fallback is active by default
- **Octoparse scrape**: 20 SA clinics seeded manually; live scraping requires Chrome Engine
- **Offline mode**: The sync queue stores proofs when Stellar is unreachable; AI tools require internet
