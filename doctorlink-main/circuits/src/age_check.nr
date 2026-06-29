// Age Eligibility Circuit
// Public inputs:  is_eligible (0|1), min_age
// Private inputs: dob_year, current_year
// Proves patient is at least min_age without revealing DOB

pub fn verify_age(dob_year: Field, current_year: Field, min_age: Field) {
    let age = current_year - dob_year;
    assert((age as u64) >= (min_age as u64));
}
