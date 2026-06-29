use ark_bn254::Fr;
use ark_ff::Field;
use ark_groth16::{r1cs_to_qap::LibsnarkReduction, prepare_verifying_key, Groth16};
use ark_relations::r1cs::{
    ConstraintSynthesizer, ConstraintSystemRef, LinearCombination, SynthesisError, Variable,
};
use ark_serialize::{CanonicalDeserialize, CanonicalSerialize};
use clap::Parser;
use rand::SeedableRng;
use serde::{Deserialize, Serialize};
use std::fs;
use std::path::Path;

type Bn254 = ark_bn254::Bn254;

// ── Age Check Circuit ──────────────────────────────────────────────
struct AgeCheckCircuit {
    dob_year: Option<Fr>,
    current_year: Option<Fr>,
    min_age: Option<Fr>,
    is_eligible: Option<Fr>,
}

impl ConstraintSynthesizer<Fr> for AgeCheckCircuit {
    fn generate_constraints(self, cs: ConstraintSystemRef<Fr>) -> Result<(), SynthesisError> {
        let dob = self.dob_year.unwrap_or(Fr::ZERO);
        let cur = self.current_year.unwrap_or(Fr::ZERO);
        let min = self.min_age.unwrap_or(Fr::ZERO);
        let elg = self.is_eligible.unwrap_or(Fr::ZERO);
        let dv = cs.new_witness_variable(move || Ok(dob))?;
        let cv = cs.new_witness_variable(move || Ok(cur))?;
        let mv = cs.new_input_variable(move || Ok(min))?;
        let ev = cs.new_input_variable(move || Ok(elg))?;
        let age_val = cur - dob;
        let diff_val = age_val - min;
        let av = cs.new_witness_variable(move || Ok(age_val))?;
        let diffv = cs.new_witness_variable(move || Ok(diff_val))?;
        cs.enforce_constraint(
            LinearCombination::from(av) + LinearCombination::from(dv) - LinearCombination::from(cv),
            LinearCombination::from(Variable::One),
            LinearCombination::zero(),
        )?;
        cs.enforce_constraint(
            LinearCombination::from(av) - LinearCombination::from(mv) - LinearCombination::from(diffv),
            LinearCombination::from(Variable::One),
            LinearCombination::zero(),
        )?;
        cs.enforce_constraint(
            LinearCombination::from(ev) - LinearCombination::from(Variable::One),
            LinearCombination::from(diffv),
            LinearCombination::zero(),
        )?;
        Ok(())
    }
}

// ── License Verify Circuit ─────────────────────────────────────────
struct LicenseVerifyCircuit {
    license_number: Option<Fr>,
    license_hash: Option<Fr>,
    is_verified: Option<Fr>,
}

impl ConstraintSynthesizer<Fr> for LicenseVerifyCircuit {
    fn generate_constraints(self, cs: ConstraintSystemRef<Fr>) -> Result<(), SynthesisError> {
        let ln = self.license_number.unwrap_or(Fr::ZERO);
        let lh = self.license_hash.unwrap_or(Fr::ZERO);
        let iv = self.is_verified.unwrap_or(Fr::ZERO);
        let ln_var = cs.new_witness_variable(move || Ok(ln))?;
        let lh_var = cs.new_input_variable(move || Ok(lh))?;
        let iv_var = cs.new_input_variable(move || Ok(iv))?;
        cs.enforce_constraint(
            LinearCombination::from(ln_var) - LinearCombination::from(lh_var),
            LinearCombination::from(iv_var),
            LinearCombination::zero(),
        )?;
        cs.enforce_constraint(
            LinearCombination::from(iv_var),
            LinearCombination::from(iv_var) - LinearCombination::from(Variable::One),
            LinearCombination::zero(),
        )?;
        Ok(())
    }
}

// ── Vaccine Status Circuit ─────────────────────────────────────────
struct VaccineStatusCircuit {
    record_hash: Option<Fr>,
    required_hash: Option<Fr>,
    is_compliant: Option<Fr>,
}

impl ConstraintSynthesizer<Fr> for VaccineStatusCircuit {
    fn generate_constraints(self, cs: ConstraintSystemRef<Fr>) -> Result<(), SynthesisError> {
        let rh = self.record_hash.unwrap_or(Fr::ZERO);
        let rqh = self.required_hash.unwrap_or(Fr::ZERO);
        let ic = self.is_compliant.unwrap_or(Fr::ZERO);
        let rh_var = cs.new_input_variable(move || Ok(rh))?;
        let rqh_var = cs.new_input_variable(move || Ok(rqh))?;
        let ic_var = cs.new_input_variable(move || Ok(ic))?;
        cs.enforce_constraint(
            LinearCombination::from(rh_var) - LinearCombination::from(rqh_var),
            LinearCombination::from(ic_var),
            LinearCombination::zero(),
        )?;
        cs.enforce_constraint(
            LinearCombination::from(ic_var),
            LinearCombination::from(ic_var) - LinearCombination::from(Variable::One),
            LinearCombination::zero(),
        )?;
        Ok(())
    }
}

// ── Helpers ────────────────────────────────────────────────────────

#[derive(Serialize, Deserialize)]
struct ProofOutput {
    proof_a_g1: Vec<String>,
    proof_b_g2: Vec<String>,
    proof_c_g1: Vec<String>,
    vk_alpha_g1: Vec<String>,
    vk_beta_g2: Vec<String>,
    vk_gamma_g2: Vec<String>,
    vk_delta_g2: Vec<String>,
    vk_gamma_abc_g1: Vec<Vec<String>>,
    public_inputs: Vec<String>,
}

fn hex_chunks<T: CanonicalSerialize>(v: &T) -> Vec<String> {
    let mut b = vec![];
    v.serialize_compressed(&mut b).unwrap();
    hex::encode(&b)
        .as_bytes()
        .chunks(64)
        .map(|c| String::from_utf8(c.to_vec()).unwrap())
        .collect()
}

fn hex_uncompressed<T: CanonicalSerialize>(v: &T) -> String {
    let mut b = vec![];
    v.serialize_uncompressed(&mut b).unwrap();
    hex::encode(&b)
}

fn fr_from_hex_prefix(s: &str) -> Fr {
    let trimmed = s.trim_start_matches("0x");
    let shortened = if trimmed.len() > 16 { &trimmed[..16] } else { trimmed };
    Fr::from(u64::from_str_radix(shortened, 16).unwrap_or(0))
}

// ── CLI ────────────────────────────────────────────────────────────

#[derive(Parser)]
#[command(name = "doctorlink-prover")]
struct Args {
    #[arg(short, long, default_value = "age_check")]
    circuit: String,

    #[arg(short = 'b', long)]
    dob_year: Option<u64>,
    #[arg(short = 'c', long)]
    current_year: Option<u64>,
    #[arg(short = 'm', long)]
    min_age: Option<u64>,

    #[arg(long)]
    license_number: Option<u64>,
    #[arg(long)]
    license_hash: Option<String>,

    #[arg(long)]
    record_hash: Option<String>,
    #[arg(long)]
    required_hash: Option<String>,

    #[arg(short = 'o', long, default_value = "proof_data")]
    out_dir: String,
    #[arg(short = 'k', long)]
    pk_path: Option<String>,
    #[arg(long, default_value_t = false)]
    stellar_hex: bool,
}

fn pk_path(circuit: &str, out_dir: &str) -> String {
    format!("{out_dir}/{circuit}_pk.bin")
}

fn load_pk<P: AsRef<Path>>(path: P, dummy: impl ConstraintSynthesizer<Fr>) -> Result<ark_groth16::ProvingKey<Bn254>, Box<dyn std::error::Error>> {
    let path = path.as_ref();
    if path.exists() {
        eprintln!("Loading proving key from {}...", path.display());
        let bytes = fs::read(path)?;
        Ok(ark_groth16::ProvingKey::<Bn254>::deserialize_uncompressed(&*bytes)?)
    } else {
        eprintln!("Generating CRS (this may take a while)...");
        let rng = &mut rand::rngs::StdRng::from_seed([0u8; 32]);
        let pk = Groth16::<Bn254, LibsnarkReduction>::generate_random_parameters_with_reduction(dummy, rng)?;
        let mut bytes = vec![];
        pk.serialize_uncompressed(&mut bytes)?;
        fs::write(path, bytes)?;
        eprintln!("Proving key saved to {}", path.display());
        Ok(pk)
    }
}

fn output_proof<C: ConstraintSynthesizer<Fr>>(
    circuit_name: &str,
    dummy_circuit: C,
    proving_circuit: C,
    public_inputs: Vec<Fr>,
    out_dir: &str,
    pk_path: &str,
) -> Result<(), Box<dyn std::error::Error>> {
    fs::create_dir_all(out_dir)?;
    let pk = load_pk(pk_path, dummy_circuit)?;

    let rng = &mut rand::rngs::StdRng::from_seed([0u8; 32]);
    let proof = Groth16::<Bn254, LibsnarkReduction>::create_random_proof_with_reduction(
        proving_circuit, &pk, rng,
    )?;

    let pvk = prepare_verifying_key(&pk.vk);
    let verified = Groth16::<Bn254, LibsnarkReduction>::verify_proof(&pvk, &proof, &public_inputs)?;
    eprintln!("Local verification: {}", verified);
    if !verified {
        eprintln!("FAILED");
        std::process::exit(1);
    }

    let a = proof.a;
    let b = proof.b;
    let c = proof.c;

    let output = ProofOutput {
        proof_a_g1: hex_chunks(&a),
        proof_b_g2: hex_chunks(&b),
        proof_c_g1: hex_chunks(&c),
        vk_alpha_g1: hex_chunks(&pk.vk.alpha_g1),
        vk_beta_g2: hex_chunks(&pk.vk.beta_g2),
        vk_gamma_g2: hex_chunks(&pk.vk.gamma_g2),
        vk_delta_g2: hex_chunks(&pk.vk.delta_g2),
        vk_gamma_abc_g1: pk.vk.gamma_abc_g1.iter().map(hex_chunks).collect(),
        public_inputs: public_inputs.iter().flat_map(hex_chunks).collect(),
    };

    let proof_path = format!("{out_dir}/{circuit_name}_proof.json");
    fs::write(&proof_path, serde_json::to_string_pretty(&output)?)?;
    eprintln!("Proof saved to {proof_path}");

    let stellar = StellarHexOutput {
        proof_a: hex_uncompressed(&a),
        proof_b: hex_uncompressed(&b),
        proof_c: hex_uncompressed(&c),
        vk_alpha: hex_uncompressed(&pk.vk.alpha_g1),
        vk_beta: hex_uncompressed(&pk.vk.beta_g2),
        vk_gamma: hex_uncompressed(&pk.vk.gamma_g2),
        vk_delta: hex_uncompressed(&pk.vk.delta_g2),
        vk_gamma_abc: pk.vk.gamma_abc_g1.iter().map(hex_uncompressed).collect(),
        public_inputs: public_inputs.iter().map(hex_uncompressed).collect(),
        circuit: circuit_name.to_string(),
    };
    println!("{}", serde_json::to_string(&stellar)?);

    if let Ok(flag) = std::env::var("STELLAR_HEX") {
        if flag == "1" {
            eprintln!("\n=== Stellar Contract Invocation ===");
            eprintln!("proof_a: {}", stellar.proof_a);
            eprintln!("proof_b: {}", stellar.proof_b);
            eprintln!("proof_c: {}", stellar.proof_c);
        }
    }

    Ok(())
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args = Args::parse();
    let pk = args.pk_path.unwrap_or_else(|| pk_path(&args.circuit, &args.out_dir));

    match args.circuit.as_str() {
        "age_check" => {
            let min = Fr::from(args.min_age.unwrap_or(18));
            let cur = Fr::from(args.current_year.unwrap_or(2026));
            let dob = Fr::from(args.dob_year.unwrap_or(1995));
            let age = cur - dob;
            let elg = Fr::from(if age >= min { 1u64 } else { 0u64 });
            eprintln!("Proving age={} >= min_age={}", age, args.min_age.unwrap_or(18));
            output_proof(
                "age_check",
                AgeCheckCircuit { dob_year: None, current_year: None, min_age: None, is_eligible: None },
                AgeCheckCircuit { dob_year: Some(dob), current_year: Some(cur), min_age: Some(min), is_eligible: Some(elg) },
                vec![min, elg],
                &args.out_dir, &pk,
            )
        }
        "license_verify" => {
            let lh_str = args.license_hash.unwrap_or_else(|| {
                let n = args.license_number.unwrap_or(12345);
                format!("{:016x}", n)
            });
            let lh = fr_from_hex_prefix(&lh_str);
            let iv = Fr::from(1u64);
            eprintln!("Proving license knowledge (hash_lo: {})", lh);
            output_proof(
                "license_verify",
                LicenseVerifyCircuit { license_number: None, license_hash: None, is_verified: None },
                LicenseVerifyCircuit { license_number: Some(lh), license_hash: Some(lh), is_verified: Some(iv) },
                vec![lh, iv],
                &args.out_dir, &pk,
            )
        }
        "vaccine_status" => {
            let rh_str = args.record_hash.unwrap_or_else(|| format!("{:016x}", 42u64));
            let rqh_str = args.required_hash.unwrap_or_else(|| format!("{:016x}", 42u64));
            let rh = fr_from_hex_prefix(&rh_str);
            let rqh = fr_from_hex_prefix(&rqh_str);
            let ic = Fr::from(if rh == rqh { 1u64 } else { 0u64 });
            eprintln!("Proving vaccine compliance: match = {}", ic == Fr::from(1u64));
            output_proof(
                "vaccine_status",
                VaccineStatusCircuit { record_hash: None, required_hash: None, is_compliant: None },
                VaccineStatusCircuit { record_hash: Some(rh), required_hash: Some(rqh), is_compliant: Some(ic) },
                vec![rh, rqh, ic],
                &args.out_dir, &pk,
            )
        }
        other => panic!("Unknown circuit: {other}"),
    }
}

#[derive(Serialize)]
struct StellarHexOutput {
    proof_a: String,
    proof_b: String,
    proof_c: String,
    vk_alpha: String,
    vk_beta: String,
    vk_gamma: String,
    vk_delta: String,
    vk_gamma_abc: Vec<String>,
    public_inputs: Vec<String>,
    circuit: String,
}
