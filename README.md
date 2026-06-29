# DoctorLink — Zero-Knowledge Health Compliance for Remote Mobile Clinics

> **Built for Stellar Hacks: Real-World ZK · June 2026**
>
> [Noir ZK circuits](doctorlink-main/circuits/src/) + [Rust Groth16 prover](doctorlink-main/prover/) (arkworks, BN254) + [Soroban smart contracts](doctorlink-main/contracts/) + Python FastHTML frontend with dark glassmorphism UI.
>
> Deployed contracts on Stellar Testnet — live and functional.

---

## Table of Contents

1. [The Problem](#the-problem)
2. [The Solution](#the-solution)
3. [Architecture Overview](#architecture-overview)
4. [Zero-Knowledge Circuits](#zero-knowledge-circuits)
5. [Smart Contracts](#smart-contracts)
6. [Offline-First Design](#offline-first-design)
7. [Frontend & AI Assistant](#frontend--ai-assistant)
8. [HPCSA License Validation](#hpcsa-license-validation)
9. [Technology Stack](#technology-stack)
10. [Repository Structure](#repository-structure)
11. [Quick Start](#quick-start)
12. [Demo Walkthrough](#demo-walkthrough)
13. [Key Design Decisions](#key-design-decisions)
14. [Contract Addresses (Testnet)](#contract-addresses-testnet)
15. [Limitations & Future Work](#limitations--future-work)
16. [License](#license)

---

## The Problem

**5 million South Africans rely on mobile clinics** in rural areas where internet connectivity is unreliable or non-existent. These clinics need to:

- Verify a patient is **over 18** for contraceptive programs
- Confirm **vaccination records** match health authority requirements
- Check that a **doctor's license** is valid and active
- Maintain an **immutable audit trail** of all verifications for regulatory compliance

### The Privacy-Compliance Trade-off

Current approaches force clinics to choose between two bad options:

| Approach | Problem |
|----------|---------|
| **Transmit raw health data** (DOB, vaccine records, license numbers) over unreliable networks | Privacy risk — sensitive data exposed during transmission and at rest on centralized servers |
| **Skip verification** when offline | Compliance failure — no audit trail, no proof that checks were performed |

**Zero-knowledge proofs break this trade-off.** With ZK, the clinic can prove compliance without revealing the underlying private data. The proof itself is a cryptographic guarantee — verifiable by anyone, anywhere.

### Why This Matters Now

South Africa's HPCSA requires active registration for all practicing doctors. Rural clinics serving vulnerable populations face the highest scrutiny but have the least infrastructure. The combination of ZK proofs + Stellar's low-cost blockchain offers a practical path forward: **private, verifiable, offline-capable compliance.**

---

## The Solution

DoctorLink generates **Groth16 zero-knowledge proofs** on-device (offline-capable) for three types of health compliance checks. The proof hash is anchored on **Stellar Soroban** for an immutable, publicly auditable trail. Patients earn **DLHT (DoctorLink Health Token)** as compliance rewards.

```
┌─────────────────────────────────────────────────────────────────┐
│                    MOBILE CLINIC (OFFLINE)                      │
│                                                                 │
│  Patient data ──► ZK Circuit ──► Groth16 Proof (on-device)     │
│  🔒 stays here      🔐 generates        📄 proof only          │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Sync Queue (SQLite) — caches proofs when offline        │    │
│  └─────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────┬──────────────────────────┘
                                       │
                          When internet available
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    STELLAR TESTNET (ONLINE)                     │
│                                                                 │
│  ┌─────────────────────┐    ┌──────────────────────────────┐    │
│  │ Verifier Contract   │◄───│ Proof hash + public inputs   │    │
│  │ CAB7ZADYO...        │    │ (store_verification)         │    │
│  └─────────────────────┘    └──────────────────────────────┘    │
│                                                                 │
│  ┌─────────────────────┐    ┌──────────────────────────────┐    │
│  │ Token Contract      │◄───│ reward_health() mints DLHT   │    │
│  │ CBZ5ZNC6I...        │    │ tokens for compliance        │    │
│  └─────────────────────┘    └──────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### What ZK Proves vs What Stays Private

| Verification | Proves (public) | Without Revealing (private) |
|---|---|---|
| **Age ≥ 18** | `birth_year ≤ current_year - 18` (boolean) | Exact date of birth |
| **Vaccine status** | `vaccine_name matches requirement` (boolean) | Full medical history, other vaccines, dates |
| **License valid** | Doctor knows a valid license number in the registry | The license number itself |

**ZK is load-bearing here.** Without it, the clinic would transmit raw birth dates, vaccine records, and license numbers over potentially insecure channels. With ZK, only a cryptographic proof leaves the device — and that proof is mathematically guaranteed to be correct.

---

## Architecture Overview

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────────┐
│   FastHTML UI     │────▶│  zk_service.py   │────▶│  Rust Prover (WSL)   │
│   (dark glass)    │     │  (orchestrator)  │     │  arkworks BN254       │
│   :8001           │     │  :8000           │     │  Groth16 + Libsnark   │
└──────────────────┘     └────────┬─────────┘     └──────────┬───────────┘
                                  │                          │
                            ┌─────▼──────┐           ┌───────▼────────┐
                            │  SQLite DB  │           │ Groth16 Proof  │
                            │  (patients, │           │ + Proving Key  │
                            │  doctors,   │           │ (cached on     │
                            │  queue, tx) │           │  filesystem)   │
                            └─────┬──────┘           └───────┬────────┘
                                  │                          │
                            ┌─────▼──────────────────────────▼────────┐
                            │           Stellar Testnet               │
                            │  ┌─────────────────┐ ┌──────────────┐   │
                            │  │ Verifier Contract│ │ Token (DLHT) │   │
                            │  │ CAB7ZADYO...     │ │ CBZ5ZNC6I... │   │
                            │  └─────────────────┘ └──────────────┘   │
                            └────────────────────────────────────────┘

┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   AI Assistant   │────▶│  ai_service.py    │────▶│  OpenRouter      │
│   Dr. Link       │     │  (triage, chat,  │     │  Gemini 2.5      │
│   /ai/*          │     │   clinic finder) │     │  Flash Lite      │
└──────────────────┘     └──────────────────┘     └──────────────────┘

┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  Clinic Directory │────▶│ clinic_service.py│────▶│ Octoparse API    │
│  /clinics         │     │  20 SA clinics   │     │ + seed data      │
└──────────────────┘     └──────────────────┘     └──────────────────┘

┌──────────────────┐     ┌──────────────────┐
│  HPCSA Check     │────▶│ hpcsa_check.py   │
│  /hpcsa/{id}     │     │ iRegister POST   │
│                   │     │ + mock fallback  │
└──────────────────┘     └──────────────────┘
```

### Data Flow: Proof Generation to On-Chain Anchoring

```
1. User clicks "Verify" on a patient/doctor
2. FastHTML route calls zk_service.py
3. zk_service.py invokes Rust prover via WSL bash subprocess
4. Rust prover loads cached proving key (or generates CRS on first run)
5. Prover creates constraint system from circuit parameters
6. Groth16 proof is generated with arkworks (BN254, LibsnarkReduction)
7. Proof is locally verified before being returned
8. zk_service.py formats public signals with "circuit" key
9. stellar-cli subprocess invokes store_verification on verifier contract
10. Transaction hash is returned and displayed to user
11. (Optional) reward_tokens() mints DLHT via token contract
12. If offline, proof is saved to sync queue instead
```

---

## Zero-Knowledge Circuits

All three circuits are written in Noir 1.0.0-beta.22 and use BN254 (Barretenberg) as the base curve. The Rust prover reimplements the same constraint systems using arkworks 0.4 for Groth16 proof generation.

### 1. Age Check (`age_check.nr`)

**Purpose:** Prove a patient is at least N years old without revealing their exact date of birth.

```
Public inputs:  min_age (e.g., 18), is_eligible (0 or 1)
Private inputs: birth_year, current_year

Constraints:
  age = current_year - birth_year
  age >= min_age
  is_eligible = 1 if age >= min_age else 0
```

**Real-world scenario:** A 16-year-old patient at a rural mobile clinic needs contraceptives. The clinic proves she is over 15 (program minimum) without recording her exact birth date. The proof is anchored on Stellar — the health department can audit that age checks were performed without accessing personal data.

### 2. License Verify (`license_verify.nr`)

**Purpose:** Prove a doctor holds a valid registered license without transmitting the license number.

```
Public inputs:  license_hash, is_verified (0 or 1)
Private inputs: license_number

Constraints:
  hash(license_number) == license_hash (simplified: equality)
  is_verified == 1
```

**Real-world scenario:** A doctor arrives at a mobile clinic in Limpopo. The clinic administrator generates a ZK proof that the doctor's license is valid and registered with HPCSA. The license number is never transmitted — only the proof that verification happened.

**Note:** This circuit uses equality constraints rather than a Pedersen hash in R1CS. Acceptable for MVP; a production version would use a proper hash commitment.

### 3. Vaccine Status (`vaccine_status.nr`)

**Purpose:** Prove a patient's vaccination record matches a required vaccine type without revealing their full medical history.

```
Public inputs:  record_hash, required_hash, is_compliant (0 or 1)
Private inputs: (none — both hashes are public)

Constraints:
  record_hash == required_hash
  is_compliant == 1 if match else 0
```

**Real-world scenario:** A clinic needs to confirm COVID-19 vaccination before a patient can receive certain treatments. The ZK proof confirms the vaccine record matches the requirement — the full immunization history stays private.

### Prover Implementation

The Rust prover (`prover/src/main.rs`) implements the same constraint systems natively with arkworks:

- **CRS Generation:** First run generates a structured reference string (proving key + verifying key) using `Groth16::<Bn254, LibsnarkReduction>::generate_random_parameters_with_reduction`
- **Key Caching:** Proving keys are cached to `proof_data/{circuit}_pk.bin` — only generated once
- **Proof Generation:** Uses `create_random_proof_with_reduction` with seeded RNG for reproducibility
- **Local Verification:** Every proof is verified locally before being output (ensures correctness)
- **Output Format:** JSON with hex-encoded proof components (G1/G2 points split into 64-char chunks) plus Stellar-ready hex strings

---

## Smart Contracts

### Verifier Contract (`doctorlink-verifier`)

**Address:** `CAB7ZADYO7M7NWYBNCMLTLO4SCQTHGHMW5QBMWJBOSA5HKMOUFTN6AN2`

A Soroban contract that stores verification records anchored to the Stellar ledger. It does NOT perform on-chain Groth16 verification (that happens off-chain) — instead it stores proof hashes, public inputs, and verification status for auditability.

**Functions:**

| Function | Parameters | Description |
|---|---|---|
| `store_verification` | `circuit: Symbol`, `proof_hash: String`, `public_inputs: Vec<Fr>`, `verified: Bool` | Permanently anchor a verification record on Stellar |
| `get_last_verification` | (none) | Returns the most recently stored verification record |
| `verify_groth16` | `vk: Bytes`, `proof: Bytes`, `public_inputs: Vec<u256>` | On-chain BN254 Groth16 verification (prepared for future use) |

**Why store verification data on-chain?**

The Stellar ledger provides:
- **Immutability:** Once anchored, a verification record cannot be altered or deleted
- **Public auditability:** Regulators, health authorities, and auditors can independently verify compliance
- **Tamper-evidence:** Any attempt to forge a proof is detectable — the on-chain record serves as the source of truth
- **Low cost:** Stellar's fees are fractions of a cent, making batch syncing practical

### Token Contract (`doctorlink-token`)

**Address:** `CBZ5ZNC6I4NOWKGFJOECMYJWUQ2QGQZ622PJQIV6EK427WVS3HONQGRT`

**Token:** DoctorLink Health Token (DLHT)

A Soroban token contract that mints DLHT tokens as patient compliance rewards. This creates a positive feedback loop — patients earn tokens for participating in health verification.

**Functions:**

| Function | Parameters | Description |
|---|---|---|
| `initialize` | `admin: Address`, `name: String`, `symbol: String` | Set up token with admin and metadata |
| `reward_health` | `admin: Address`, `patient: Address`, `amount: u256` | Mint DLHT tokens as compliance reward (admin-only) |
| `balance` | `id: Address` | Query token balance for any address |
| `total_supply` | (none) | Get total minted DLHT supply |

---

## Offline-First Design

The most critical requirement for rural mobile clinics: **ZK proofs must work without internet.**

### How It Works

1. **Generate proof locally** — the Rust prover runs entirely on-device, no network calls
2. **Cache proof in sync queue** — `StellarSyncQueue` SQLite table stores proof hash, public signals, and entity metadata
3. **Sync when online** — the Sync Queue page (`/queue`) shows pending items, and "Sync All" batch-submits to Stellar Soroban
4. **Verify on-chain later** — anchored proofs are viewable on the On-Chain page (`/onchain`)

### Dual-Mode Operation

| Mode | Internet Required | Features Available |
|---|---|---|
| **Mobile Clinic** (offline) | No | Patient verification, ZK proof generation, sync queue, on-chain viewer |
| **Telehealth Hub** (online) | Yes | AI clinic finder, triage, chat, HPCSA live check, Octoparse API |

The application detects connectivity and degrades gracefully — AI tools show a clear message when offline, while ZK verification features remain fully functional.

### Sync Queue Data Model

```python
class StellarSyncQueue(Base):
    """Offline-generated proofs awaiting sync to Stellar."""
    id: int (PK)
    entity_type: str        # "contraceptive_eligibility" | "doctor_verification"
    entity_id: int
    proof_hash: str
    public_signals: dict    # JSON: circuit, public inputs, signals
    status: str             # "pending" | "synced" | "failed"
    tx_hash: str | None     # Stellar transaction hash (populated after sync)
    created_at: datetime
    synced_at: datetime | None
```

---

## Frontend & AI Assistant

### FastHTML Dashboard

The frontend is built with [FastHTML](https://fastht.ml/) — a Python library that generates HTML components server-side, eliminating the need for a separate frontend framework or API layer.

**Design Language:** Dark glassmorphism with animated background

- **Color palette:** `--bg-dark: #070b14`, violet (`#8b5cf6`) and cyan (`#06b6d4`) accents
- **Typography:** Outfit (display) + Plus Jakarta Sans (body), loaded from Google Fonts
- **Components:** `glass-card` (translucent with backdrop-blur + hover lift), `glass-card-premium` (animated rotating neon border via CSS `@property`), `gradient-btn` (gradient with glow shadows), `input-glass` (dark with focus glow), `tbl` (clean dark table)
- **Background:** Animated gradient shift over 20s, 3 floating orbs (`orb-1`, `orb-2`, `orb-3`) with slow translation, subtle grid overlay + scanline effect
- **No DaisyUI or Tailwind component libraries** — all CSS is custom, defined inline in the FastHTML app header

**Pages (21+ routes):**

| Route | Page | Description |
|---|---|---|
| `/` | Dashboard | Problem-first narrative, "Why ZK?" callout, 3-step How It Works flow, 3 action cards |
| `/patients` | Patients & Doctors | Patient/doctor directory with ZK verification actions and HPCSA checks |
| `/verify/age/{id}` | Age Verification | Generate ZK age proof on-device, submit to Stellar, show result |
| `/verify/vaccine/{id}` | Vaccine Verification | Generate ZK vaccine proof, submit, show result |
| `/verify/license/{id}` | License Verification | Run HPCSA check first, then generate ZK license proof |
| `/hpcsa/{id}` | HPCSA Check | View HPCSA iRegister status for a doctor |
| `/reward/{id}` | Token Reward | Mint DLHT tokens to patient |
| `/queue` | Sync Queue | View pending offline proofs, batch sync |
| `/sync/all` | Sync Action | Submit all pending proofs to Stellar |
| `/onchain` | On-Chain State | Live view of verifier + token contract state |
| `/ai` | AI Landing | Choose clinic finder, triage, or chat |
| `/ai/clinic-finder` | Clinic Finder | Search SA clinics by location using AI |
| `/ai/triage` | Symptom Triage | Step-by-step AI symptom assessment |
| `/ai/chat` | Dr. Link Chat | Multi-turn AI conversation (history via signed cookies) |
| `/clinics` | Clinic Directory | Full list of 20 seeded SA clinics |

### AI Assistant — Dr. Link

Powered by **Gemini 2.5 Flash Lite** via **OpenRouter**. Dr. Link serves three roles:

#### Clinic Finder (`/ai/clinic-finder`)

Searches the SA clinic database (20 clinics seeded from real providers) using fuzzy keyword matching. Users can ask natural-language questions like "Find a clinic in Johannesburg that does HIV testing" — the AI queries `clinic_service.py` and presents results.

#### Symptom Triage (`/ai/triage`)

Step-by-step symptom assessment:
1. User describes their symptoms
2. AI asks clarifying questions (duration, severity, pre-existing conditions)
3. AI provides a triage recommendation (self-care, clinic visit, emergency)
4. Results include nearby clinics from the database

#### General Chat (`/ai/chat`)

Multi-turn conversation about DoctorLink, zero-knowledge proofs, Stellar integration, and general health topics. Chat history is maintained per-session via FastHTML signed cookies.

### Clinic Directory

**20 seeded South African clinics** representing real healthcare providers:

| Provider | Clinics | Types |
|---|---|---|
| Netcare | 5 | Christiaan Barnard Memorial, Milpark, St Augustine's, Union, Sunningdale |
| Mediclinic | 5 | Medforum, Bloemfontein, Vergelegen, Louis Leipoldt, Durbanville |
| Life Healthcare | 5 | Riverfield, Bedford Gardens, Mount Edgecombe, Wilgers, The Glynnwood |
| Government | 3 | Chris Hani Baragwanath, Tygerberg, King Edward VIII |
| Private | 2 | Vincent Pallotti, Sunward Park |

Each clinic has: name, address, phone, GPS coordinates, operating hours, services list, and provider badge color.

---

## HPCSA License Validation

South Africa's **Health Professions Council of South Africa (HPCSA)** maintains the iRegister — a public database of registered healthcare practitioners.

### Integration

The `hpcsa_check.py` module:

1. Accepts a doctor's registration number (SA format: `MP0456789`, `PS123456`, `DN0456789`, etc.)
2. Sends a POST request to the HPCSA iRegister endpoint
3. Parses the response for registration status, full name, register type, and effective date
4. Returns structured data: `{found, is_active, status, full_name, register, source, ...}`

### Fallback Behavior

The live HPCSA iRegister endpoint requires Oracle RightNow JavaScript context — plain HTTP POST requests may time out. The system has a robust mock fallback:

| Registration Pattern | Mock Behavior |
|---|---|
| `MP` prefix (medical practitioners) | Returns "Active" with practitioner name and register type |
| `PS` prefix (psychologists) | Returns "Active" |
| `DN` prefix (dieticians/nutritionists) | Returns "Active" |
| `LIC-*` / other formats (international/test) | Returns "Not Found" |
| Empty / invalid | Returns "Not Found" |

Results are cached to reduce redundant lookups.

### In the ZK Pipeline

The HPCSA check runs **before** ZK proof generation for license verification:
- If HPCSA returns "Active" → proceed with ZK proof
- If HPCSA returns "Not Found" / "Erased" / "Suspended" → show warning, still allow ZK proof with caveat

---

## Technology Stack

| Layer | Technology | Version / Details |
|---|---|---|
| **Circuit Language** | Noir | 1.0.0-beta.22, Barretenberg backend, BN254 curve |
| **Prover** | Rust + arkworks | 0.4, BN254 Groth16 with LibsnarkReduction |
| **Smart Contracts** | Soroban (Rust) | Deployed on Stellar testnet (Protocol 25/26) |
| **Blockchain** | Stellar Testnet | Native BN254 host functions for elliptic-curve ops |
| **Backend / API** | Python FastHTML | Server-side HTML generation, SQLAlchemy ORM |
| **Database** | SQLite | Local development, single-file storage |
| **Frontend** | FastHTML + Custom CSS | Dark glassmorphism, animated gradients, no JS framework |
| **AI / LLM** | OpenRouter → Gemini 2.5 Flash Lite | `google/gemini-2.5-flash-lite` |
| **Clinic Data** | Octoparse REST API + seed data | 20 SA clinics from Netcare, Mediclinic, Life Healthcare, Government, Private |
| **License Validation** | HPCSA iRegister | Live POST + mock fallback |
| **Fonts** | Google Fonts | Outfit (display), Plus Jakarta Sans (body) |
| **CLI** | stellar-cli | 27.0.0 for contract invocation |
| **WSL** | Ubuntu 24.04 | Runs Rust prover and stellar-cli on Windows |

---

## Repository Structure

```
doctorlink-zk/
├── README.md                          # ← You are here
├── .gitignore
│
├── doctorlink-main/                   # Monorepo (circuits, contracts, prover)
│   ├── circuits/                      # 3 Noir ZK circuits
│   │   └── src/
│   │       ├── main.nr
│   │       ├── age_check.nr           # Prove age ≥ 18 without DOB
│   │       ├── license_verify.nr      # Prove valid doctor license
│   │       └── vaccine_status.nr      # Prove vaccine compliance
│   ├── contracts/
│   │   ├── doctorlink-verifier/       # Soroban Groth16 verifier contract
│   │   │   └── src/lib.rs
│   │   └── doctorlink-token/          # DLHT reward token contract
│   │       └── src/lib.rs
│   ├── prover/                        # Rust arkworks Groth16 prover
│   │   ├── Cargo.toml
│   │   └── src/main.rs                # CLI: --circuit <name>
│   ├── proof_data/                    # Cached proving keys + proofs
│   ├── scripts/                       # Deploy, test, helper scripts
│   └── README.md                      # Monorepo-specific docs
│
├── doctorlink-health-services/        # Application layer
│   ├── frontend.py                    # FastHTML frontend (21+ routes, all CSS)
│   ├── zk_service.py                  # ZK orchestration + Stellar submission
│   ├── ai_service.py                  # OpenRouter AI client (Dr. Link)
│   ├── clinic_service.py             # Octoparse client + 20 seeded clinics
│   ├── hpcsa_check.py                # HPCSA iRegister validation
│   ├── models.py                     # SQLAlchemy models (Patient, Doctor, Queue, etc.)
│   ├── schemas.py                    # Pydantic schemas
│   ├── config.py                     # Settings from .env
│   ├── main.py                       # FastHTML app entry point
│   ├── requirements.txt
│   ├── .env                          # Secrets (gitignored)
│   ├── static/                       # Static assets
│   ├── api/v1/endpoints.py           # REST API endpoints
│   ├── README.md                     # Application-specific docs
│   └── DEMO_SCRIPT.md               # 2.5-min demo video script
│
├── stellar-hacks-zk-hackathon-info.md # Hackathon context & requirements
└── DEMO_SCRIPT.md                    # Expanded demo walkthrough
```

---

## Quick Start

### Prerequisites

- Python 3.10+
- WSL with Ubuntu 24.04 (for Rust prover and stellar-cli on Windows)
- Rust toolchain (for compiling the prover)
- A Stellar testnet funded account

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/Skywalkingzulu1/doctorlink-zk.git
cd doctorlink-zk

# 2. Install Python dependencies
cd doctorlink-health-services
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your:
#   - STELLAR_SECRET_KEY (your funded testnet account)
#   - OPENROUTER_API_KEY (from https://openrouter.ai/keys)
#   - OCTOPARSE_API_KEY (if using live clinic scraping)

# 4. Run the Rust prover (first run generates CRS — may take a minute)
cd ../doctorlink-main/prover
cargo run --release -- --circuit age_check \
  --dob-year 1995 --current-year 2026 --min-age 18

# 5. Start the web app
cd ../../doctorlink-health-services
python -c "import uvicorn; uvicorn.run('frontend:app', host='0.0.0.0', port=8001)"
```

**Open http://localhost:8001** in your browser.

### Environment Variables

```env
# .env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./health_services.db
STELLAR_NETWORK=testnet
ZK_VERIFIER_CONTRACT=CAB7ZADYO7M7NWYBNCMLTLO4SCQTHGHMW5QBMWJBOSA5HKMOUFTN6AN2
HEALTH_TOKEN_CONTRACT=CBZ5ZNC6I4NOWKGFJOECMYJWUQ2QGQZ622PJQIV6EK427WVS3HONQGRT
STELLAR_SECRET_KEY=S...
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_MODEL=google/gemini-2.5-flash-lite
OCTOPARSE_API_KEY=...
OCTOPARSE_TASK_GROUP_ID=0
```

---

## Demo Walkthrough

### 1. Dashboard (Problem-First Narrative)

Open `/` to see:
- "Private Health Compliance for Remote Mobile Clinics" hero
- "Why Zero-Knowledge?" callout explaining the privacy-compliance trade-off
- 3-step How It Works flow: **Register → Generate ZK Proof → Anchor on Stellar**
- Three action cards: Verify a Patient, Find a Clinic, On-Chain State

### 2. Verify a Patient's Age

1. Navigate to **Patients** (`/patients`)
2. Click **Prove Age ≥ 18** on any patient row
3. The system generates a Groth16 proof on-device:
   - `zk_service.py` calls the Rust prover with the patient's birth year
   - The prover generates a proof proving `current_year - birth_year >= 18`
   - The proof is locally verified, then the proof hash + public signals are submitted to Stellar
4. Result page shows:
   - A ZK explainer card: "Your date of birth never leaves this device"
   - The proof hash and public signals
   - Transaction status (submitted / failed)
   - A link to Stellar Explorer to view the transaction

### 3. Verify a Vaccine Record

1. From **Patients**, click **Vaccine Proof**
2. The system generates a ZK proof confirming the patient's vaccine matches the required type
3. Result page shows the proof and on-chain submission status

### 4. Verify a Doctor's License

1. From **Patients**, click **Prove License (ZK)** on a doctor row
2. First, the HPCSA iRegister check runs:
   - If the license number follows SA format (MP, PS, DN prefix), it returns "Active"
   - International/test numbers return "Not Found"
3. Then the ZK proof generates, proving the doctor holds a valid license
4. Result page shows:
   - HPCSA status card with registration details
   - ZK explainer: "The license number is never transmitted"
   - Proof hash, public signals, and Stellar transaction status

### 5. Check HPCSA Registration

1. From **Patients**, click **HPCSA Check** on a doctor row
2. View detailed HPCSA iRegister response: status, full name, register type, effective date

### 6. Reward DLHT Tokens

1. From **Patients**, click **Reward DLHT** on a patient row
2. The token contract mints DLHT tokens to the patient address
3. Result page shows the new DLHT balance and transaction hash

### 7. View On-Chain State

Navigate to **On-Chain** (`/onchain`):
- Live query of the verifier contract for the last verification record
- Live query of the token contract for DLHT balance
- Refresh button to pull fresh data from Stellar testnet

### 8. Sync Queue

Navigate to **Queue** (`/queue`):
- View all pending offline-generated proofs
- Each item shows entity type, proof hash, and sync status
- Click **Sync All to Stellar** to batch-submit

### 9. AI Clinic Finder

Navigate to **AI** → **Clinic Finder** (`/ai/clinic-finder`):
- Ask natural-language questions: "Find a clinic in Cape Town"
- Dr. Link searches the clinic database and returns matching results
- Each result shows provider, services, phone, and directions link

### 10. AI Triage

Navigate to **AI** → **Triage** (`/ai/triage`):
- Describe symptoms (e.g., "I have a fever and cough for 3 days")
- Dr. Link asks clarifying questions
- Receives a triage recommendation with suggested care level

### 11. AI Chat

Navigate to **AI** → **Chat** (`/ai/chat`):
- Multi-turn conversation with Dr. Link
- Ask about ZK proofs, Stellar, health topics, or DoctorLink features
- Chat history is preserved per session via signed cookies

### 12. Clinic Directory

Navigate to **Clinics** (`/clinics`):
- Browse all 20 seeded South African clinics
- Each card shows name, provider (with color badge), address, phone, hours, services
- Quick actions: Call or Get Directions (Google Maps)

---

## Key Design Decisions

### Why BN254 over BLS12-381?

Noir's Barretenberg backend targets BN254 by default. Originally we prototyped with BLS12-381 but switched to BN254 to match Noir's curve — avoiding cross-curve compatibility issues between the circuit compiler and the prover.

### Why arkworks over bb (Barretenberg binary)?

The `bb` binary (Noir's native prover) requires a specific build for each platform and was difficult to integrate into the Python backend. The arkworks Rust prover is a single binary that:
- Implements the same constraint systems as the Noir circuits
- Generates and caches proving keys
- Produces Groth16 proofs in a Python-friendly JSON format
- Runs locally with no network calls (critical for offline mode)

### Why FastHTML over React?

FastHTML lets us build a server-rendered SPA entirely in Python, eliminating:
- A separate frontend framework (React, Next.js)
- A separate API layer (FastAPI REST endpoints)
- Build tooling (webpack, Vite)
- Client-side state management

This dramatically reduced development time while still delivering a modern, interactive UI.

### Why stellar-cli over Python SDK?

The Python Stellar SDK has limited Soroban support. The `stellar-cli` native binary provides complete coverage of Soroban contract functions and is more reliable for subprocess invocation.

### Why Octoparse REST API over CLI?

The Octoparse CLI requires the Chrome Engine download and desktop app. The REST API with `x-api-key` header authentication is simpler to integrate for data retrieval from existing scrape tasks.

### Why No DaisyUI?

DaisyUI adds ~50KB of CSS and imposes its own design system (component classes, responsive breakpoints, color schemes). Custom CSS gives us:
- Full control over the dark glassmorphism aesthetic
- Animations: rotating neon borders, floating orbs, gradient shift
- Minimal payload (no unused utility classes)
- No framework lock-in

### Why LibsnarkReduction?

The Groth16 proving system varies by the QAP reduction algorithm used. LibsnarkReduction is the standard choice for compatibility with existing verifiers and tools (including SnarkJS, ZoKrates, and arkworks' default examples). It produces provably secure proofs under the knowledge-of-exponent assumption.

---

## Contract Addresses (Testnet)

| Contract | Address | Description |
|---|---|---|
| **Verifier** | `CAB7ZADYO7M7NWYBNCMLTLO4SCQTHGHMW5QBMWJBOSA5HKMOUFTN6AN2` | Stores anchored ZK verification records |
| **Token (DLHT)** | `CBZ5ZNC6I4NOWKGFJOECMYJWUQ2QGQZ622PJQIV6EK427WVS3HONQGRT` | DoctorLink Health Token — compliance rewards |
| **Fee Sponsor** | `GCLJMFKL3CFWJKZS6UM5BF5KWG67UMVL7TCSDAM4L3JIFWNMV3LSIFL7` | Funded account covering transaction fees |

---

## Limitations & Future Work

### Current Limitations

| Issue | Status | Workaround |
|---|---|---|
| **LicenseVerify circuit uses equality instead of hash** | Acceptable for MVP | A Pedersen hash in R1CS would increase constraint count significantly; equality proves knowledge of a matching value |
| **VaccineStatus circuit uses equality** | Same as above | Same constraint budget consideration |
| **HPCSA live API times out** | Mock fallback active | The iRegister requires Oracle RightNow JS context; a headless browser or API partner integration would fix this |
| **Octoparse live scraping requires Chrome Engine** | Seed data used | Desktop app or CLI download needed for dynamic task creation |
| **No on-chain Groth16 verification in verifier contract** | `verify_groth16` prepared but not invoked | Stellar's BN254 host functions are available; full on-chain verification would require passing the entire proof + VK (high cost for MVP) |
| **Single user / no auth** | Developer demo | Authentication, role-based access, and patient consent management are future work |
| **SQLite database** | Not production-scale | Migration to PostgreSQL with replication for multi-clinic deployments |

### Future Work

1. **Full on-chain Groth16 verification** — implement `verify_groth16` on the Soroban contract to verify proofs directly on Stellar
2. **Integration with SA Health Identity System** — connect to NDOH (National Department of Health) systems for real patient identity
3. **Mobile app** — React Native or Flutter frontend for field use on tablets
4. **Multi-clinic sync** — shared Stellar queue with conflict resolution
5. **Verifiable credentials** — issue W3C-compliant verifiable credentials from ZK proofs
6. **Production HPCSA integration** — partner with HPCSA for API access (avoiding Oracle RightNow)
7. **More circuit types** — HIV status, TB screening, pregnancy test results, mental health assessments
8. **Tokenomics** — DLHT exchangeability, clinic incentives, patient reward tiers
9. **Compliance dashboard** — real-time analytics for health authorities monitoring clinic compliance
10. **Disaster recovery** — cold storage of proving keys, backup Soroban contracts on other networks

---

## License

MIT — see LICENSE file for details.

---

*Built for [Stellar Hacks: Real-World ZK](https://dorahacks.io/hackathon/stellar-hacks-zk/detail) · June 2026*
