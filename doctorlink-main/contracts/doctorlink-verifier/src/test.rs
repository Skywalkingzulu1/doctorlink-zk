#![cfg(test)]

use super::*;
use soroban_sdk::{vec, Env, String};

#[test]
fn test_storage() {
    let env = Env::default();
    let contract_id = env.register_contract(None, DoctorLinkVerifier);

    let inputs = vec![&env, Fr::from_u64(&env, 42)];

    let client = DoctorLinkVerifierClient::new(&env, &contract_id);
    client.store_verification(
        &CircuitType::AgeEligibility,
        &String::from_str(&env, "proof_hash_abc"),
        &inputs,
        &true,
    );

    let record = client.get_last_verification();
    assert!(record.is_some());
    let r = record.unwrap();
    assert!(r.verified);
    assert_eq!(r.proof_hash, String::from_str(&env, "proof_hash_abc"));
}
