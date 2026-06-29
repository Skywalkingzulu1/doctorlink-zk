mod age_check;
mod license_verify;
mod vaccine_status;

fn main(dob_year: pub Field, current_year: pub Field, min_age: pub Field) {
    age_check::verify_age(dob_year, current_year, min_age);
}
