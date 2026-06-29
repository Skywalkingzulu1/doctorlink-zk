# DoctorLink Agent Integration Protocol

This document defines the interface standards, roles, skills, and operational constraints for autonomous AI agents (e.g., Kilo, audit agents) interacting with the **DoctorLink Zero-Knowledge (ZK) Compliance Engine** and the **Stellar ledger**.

---

## 🤖 Agent Roles & Security Profiles

### 1. Verification Auditor Agent
* **Purpose**: Performs periodic checks on doctor licensing credentials and clinic compliance.
* **Access Level**: Public signals, proof hashes, and Stellar ledger transactions.
* **Primary Activities**:
  * Scans registered doctors in the directory.
  * Triggers ZK-proof generation for unverified licenses.
  * Inspects the on-chain Soroban contract to audit compliance proofs.
* **HIPAA/GDPR Boundary**: Can *never* access private keys, plaintext license details, or raw medical logs.

### 2. Healthcare Advisor Agent
* **Purpose**: Coordinates patient consultations, vaccine scheduling, and treatment recommendations.
* **Access Level**: Local patient profiles (with consent) and ZK eligibility interfaces.
* **Primary Activities**:
  * Assesses vaccine schedules and flags overdue doses.
  * Queries the ZK Service to check if a patient meets contraceptive program criteria.
  * Issues prescriptions once eligibility is cryptographically attested.

---

## 🛠️ Agent Skills & Tool APIs

AI Agents can interface with the Trust Engine using the following endpoints and parameters:

### 1. Contraceptive Program Eligibility Check
* **Tool Name**: `check_contraceptive_eligibility`
* **Endpoint**: `POST /api/v1/contraceptives`
* **Description**: Initiates client-side ZK-proof proving that the patient matches program safety parameters (age & gender) without exposing dates of birth or gender records to the network payload.
* **Parameters**:
  * `patient_id` (integer)
  * `contraceptive_type` (string)
  * `brand_name` (string)
  * `offline` (boolean, defaults to `false`)

### 2. Doctor Credential Verification
* **Tool Name**: `verify_doctor_licensing`
* **Endpoint**: `POST /api/v1/verifications`
* **Description**: Runs a ZK proving circuit on the doctor's license number, outputs a proof hash, and registers the verification status.
* **Parameters**:
  * `doctor_id` (integer)
  * `verification_type` (string)
  * `provider` (string)
  * `offline` (boolean, defaults to `false`)

### 3. Ledger Synchronization Auditor
* **Tool Name**: `reconcile_offline_proofs`
* **Endpoint**: `POST /api/v1/sync/stellar`
* **Description**: Scans the cached sync queue for offline-generated proofs and commits them to the Stellar Soroban smart contract.

### 4. HPCSA Registration Checker
* **Tool Name**: `check_hpcsa_registration`
* **Endpoint**: `GET /api/v1/hpcsa/{doctor_id}` (or via frontend: `GET /hpcsa/{doctor_id}`)
* **Description**: Validates a doctor's license number against the HPCSA iRegister before ZK proof generation. Returns registration status (Active/Erased/Suspended/Not Found).
* **Fallback**: If HPCSA server is unreachable, returns mock data for known SA-format numbers (MP, PS, DN prefixes) or "Not Found" for international/fake numbers.

---

## 🛑 Operational Constraints (Safety Boundaries)

Agents must strictly adhere to the following rules during autonomous workflows:

### Rule 1: Privacy Preservation
Patient safety checks must go exclusively through the ZK verification service. Agents must never query or log private patient identifiers (DOB, Gender) directly in public logs or API request payloads.

### Rule 2: Offline-First Awareness
Mobile clinics in remote areas operate disconnected from the internet. When writing prescriptions or verifications off-grid, agents must set the `offline` parameter to `true`. This caches the proof in the queue, preventing request timeouts.

### Rule 3: Sync Priority
Before compiling daily clinic reports or closing an audit, the Auditor Agent must check `GET /api/v1/sync/queue`. If pending items exist, it must trigger `POST /api/v1/sync/stellar` to ensure all ZK verifications are successfully anchored to the Stellar ledger.

### Rule 4: HPCSA Pre-Check for SA Doctors
When verifying a doctor with an SA-format registration number (`MP`, `PS`, `DN`, etc. prefix), always run the HPCSA check first via `GET /hpcsa/{doctor_id}`. Only proceed to ZK proof generation if the HPCSA status is "Active". For international/fake license numbers (`LIC-...`), the HPCSA check will return "Not Found" — document this in the audit log.

### Rule 5: Dual-Mode Awareness
DoctorLink operates in two modes:
- **Telehealth Hub** (online): AI-powered clinic finder, triage, and general chat. Routes under `/ai/*`. Requires internet connection to call OpenRouter API. Available in the navbar as "AI Assistant".
- **Mobile Clinic** (offline-first): Patient verification, ZK proof generation, sync queue, on-chain state. Routes under `/patients`, `/verify/*`, `/queue`, `/sync/*`, `/onchain`, `/reward/*`. Works without internet; syncs to Stellar when connection becomes available.

When an agent detects the system is offline, it must:
1. Inform the user that AI tools are unavailable in offline mode
2. Direct the user to the Mobile Clinic dashboard (`/`) for ZK verification tools
3. Queue any generated proofs for later sync

---

## 📝 Example Agent Tool Definition (JSON Schema)

```json
{
  "name": "check_contraceptive_eligibility",
  "description": "Verifies patient program eligibility using a Zero-Knowledge safety check without revealing private demographics.",
  "parameters": {
    "type": "object",
    "properties": {
      "patient_id": { "type": "integer", "description": "The unique database ID of the patient" },
      "contraceptive_type": { "type": "string", "description": "Category of contraceptive program (e.g. Oral Contraceptive Pill)" },
      "brand_name": { "type": "string", "description": "Specified brand name of the drug" },
      "offline": { "type": "boolean", "description": "Set to true if operating off-grid in a mobile clinic unit" }
    },
    "required": ["patient_id", "contraceptive_type", "brand_name"]
  }
}
```
