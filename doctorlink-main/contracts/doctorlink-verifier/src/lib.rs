#![no_std]
use soroban_sdk::{
    contract, contracterror, contractimpl, contracttype,
    crypto::bn254::{Bn254G1Affine, Bn254G2Affine, Fr},
    vec, Env, String, Vec, symbol_short,
};

#[contracterror]
#[derive(Copy, Clone, Debug, Eq, PartialEq, PartialOrd, Ord)]
#[repr(u32)]
pub enum VerifierError {
    MalformedVerifyingKey = 0,
    InvalidProof = 1,
}

#[derive(Clone)]
#[contracttype]
pub struct Groth16VerifyingKey {
    pub alpha: Bn254G1Affine,
    pub beta: Bn254G2Affine,
    pub gamma: Bn254G2Affine,
    pub delta: Bn254G2Affine,
    pub ic: Vec<Bn254G1Affine>,
}

#[derive(Clone)]
#[contracttype]
pub struct Groth16Proof {
    pub a: Bn254G1Affine,
    pub b: Bn254G2Affine,
    pub c: Bn254G1Affine,
}

#[derive(Clone)]
#[contracttype]
pub enum CircuitType {
    AgeEligibility,
    LicenseVerify,
    VaccineStatus,
}

#[derive(Clone)]
#[contracttype]
pub struct VerificationRecord {
    pub circuit: CircuitType,
    pub proof_hash: String,
    pub public_inputs: Vec<Fr>,
    pub verified: bool,
    pub timestamp: u64,
}

#[contract]
pub struct DoctorLinkVerifier;

#[contractimpl]
impl DoctorLinkVerifier {
    pub fn verify_groth16(
        env: Env,
        vk: Groth16VerifyingKey,
        proof: Groth16Proof,
        public_inputs: Vec<Fr>,
    ) -> Result<bool, VerifierError> {
        let bn254 = env.crypto().bn254();

        if public_inputs.len() + 1 != vk.ic.len() {
            return Err(VerifierError::MalformedVerifyingKey);
        }

        let mut vk_x = vk.ic.get(0).unwrap();
        for (signal, vk_ic) in public_inputs.iter().zip(vk.ic.iter().skip(1)) {
            let prod = bn254.g1_mul(&vk_ic, &signal);
            vk_x = bn254.g1_add(&vk_x, &prod);
        }

        let neg_a = -proof.a;
        let pairing_g1 = vec![&env, neg_a, vk.alpha, vk_x, proof.c];
        let pairing_g2 = vec![&env, proof.b, vk.beta, vk.gamma, vk.delta];

        Ok(bn254.pairing_check(pairing_g1, pairing_g2))
    }

    pub fn verify_age_eligibility(
        env: Env,
        proof: Groth16Proof,
        min_age: Fr,
        is_eligible: Fr,
        vk: Groth16VerifyingKey,
    ) -> Result<bool, VerifierError> {
        let public_inputs = vec![&env, min_age, is_eligible];
        Self::verify_groth16(env, vk, proof, public_inputs)
    }

    pub fn verify_license(
        env: Env,
        proof: Groth16Proof,
        license_hash: Fr,
        is_verified: Fr,
        vk: Groth16VerifyingKey,
    ) -> Result<bool, VerifierError> {
        let public_inputs = vec![&env, license_hash, is_verified];
        Self::verify_groth16(env, vk, proof, public_inputs)
    }

    pub fn verify_vaccination(
        env: Env,
        proof: Groth16Proof,
        patient_hash: Fr,
        is_compliant: Fr,
        vk: Groth16VerifyingKey,
    ) -> Result<bool, VerifierError> {
        let public_inputs = vec![&env, patient_hash, is_compliant];
        Self::verify_groth16(env, vk, proof, public_inputs)
    }

    pub fn store_verification(
        env: Env,
        circuit: CircuitType,
        proof_hash: String,
        public_inputs: Vec<Fr>,
        verified: bool,
    ) {
        let record = VerificationRecord {
            circuit,
            proof_hash,
            public_inputs,
            verified,
            timestamp: env.ledger().timestamp(),
        };
        env.storage().persistent().set(&symbol_short!("v_record"), &record);
    }

    pub fn get_last_verification(env: Env) -> Option<VerificationRecord> {
        env.storage().persistent().get(&symbol_short!("v_record"))
    }
}

#[cfg(test)]
mod test;
