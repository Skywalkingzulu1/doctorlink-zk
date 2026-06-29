# Demo Video Script (2-3 min)

## Title: DoctorLink — Private Health Compliance for Remote Clinics

---

### 0:00 – 0:30 — The Problem

**Visual**: Split screen — rural clinic on one side, dashboard on the other.

> "In South Africa, 5 million people rely on mobile clinics in rural areas where internet is unreliable. These clinics need to verify patient age, vaccine status, and doctor licenses — but current approaches expose sensitive health data over weak networks, or simply stop working when offline."

**Cut to**: Dashboard landing page

> "DoctorLink solves this with zero-knowledge proofs. The clinic generates proofs on a local device — no internet required — and anchors them on Stellar for an immutable audit trail."

---

### 0:30 – 1:15 — The ZK Flow

**Visual**: Dashboard → Patients page

> "Let me show you how it works. Here's the dashboard — we have test patients and doctors pre-loaded."

**Click "Prove Age ≥ 18" on a patient.**

> "I'll click 'Prove Age ≥ 18' on this patient. Watch what happens behind the scenes."

**Cut to**: Verification result page (or PiP showing terminal)

> "A Noir ZK circuit runs on-device, generating a Groth16 proof that confirms the patient is over 18 — without ever revealing their date of birth. That proof hash is submitted to our Soroban verifier contract on Stellar testnet."

**Point to**: "ZK proof — DOB never leaves device" callout

> "The callout here says it clearly: the date of birth never leaves this device. Only the proof is transmitted."

---

### 1:15 – 1:45 — On-Chain Verification

**Visual**: Navigate to On-Chain page

> "Now let's verify the proof was stored. I'll open the On-Chain page — it pulls live data from Stellar testnet."

**Show**: Verifier contract data + DLHT balance

> "The verifier contract shows the last verification record. And here's the DLHT token balance — patients earn these tokens as compliance rewards."

**Click "Reward DLHT" on a patient**

> "I'll reward this patient with DLHT tokens. The balance updates in real-time."

---

### 1:45 – 2:15 — Offline Queue & HPCSA

**Visual**: Queue page

> "What if the clinic is completely offline? Proofs are cached in the sync queue. When connectivity returns, one click syncs everything to Stellar."

**Show**: HPCSA check on a doctor

> "For South African doctors, we integrate with the HPCSA iRegister to validate licenses before generating ZK proofs — ensuring only actively registered practitioners are verified."

---

### 2:15 – 2:45 — AI Assistant & Wrap

**Visual**: Clinic Finder / Triage

> "When the clinic has internet, our AI assistant Dr. Link helps with symptom triage, clinic recommendations, and general health questions — powered by Gemini 2.5 Flash Lite via OpenRouter."

**Cut to**: Dashboard summary

> "Three Noir ZK circuits, a Rust Groth16 prover on BN254, two deployed Soroban contracts, and a dark glassmorphism frontend — all working end-to-end. Built for Stellar Hacks: Real-World ZK."

---

## Recording Tips
- Use OBS or Loom
- Keep mouse movements slow and deliberate
- PiP the terminal showing `stellar contract invoke` output during proof submission
- Highlight the "DOB never leaves device" callout with a cursor pause
- End with the URL: `http://localhost:8001`
