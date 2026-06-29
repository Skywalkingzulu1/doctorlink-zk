// Doctor License Verification Circuit
// Public inputs:  is_verified (0|1), license_hash
// Private inputs: license_number
// Proves doctor holds a license matching a public hash

pub fn verify_license(license_number: Field, license_hash: Field) {
    let computed_hash = std::hash::pedersen_hash([license_number]);
    assert(computed_hash == license_hash);
}
