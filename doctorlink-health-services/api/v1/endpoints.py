"""DoctorLink Health Services - API Endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from models import get_db, Appointment, Patient, Doctor, Vaccination, ContraceptiveRecord, DoctorVerification, StellarSyncQueue
from schemas import (
    PatientCreate, PatientResponse,
    DoctorCreate, DoctorResponse,
    AppointmentCreate, AppointmentResponse, AppointmentUpdate,
    VaccinationCreate, VaccinationResponse, VaccinationAdminister,
    ContraceptiveCreate, ContraceptiveResponse, ContraceptiveUpdate,
    DoctorVerificationCreate, DoctorVerificationResponse,
    StellarSyncQueueResponse,
)
from zk_service import get_zk_service, ProofError

router = APIRouter()


# ============== PATIENT ENDPOINTS ==============

@router.post("/patients", response_model=PatientResponse)
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    db_patient = Patient(**patient.model_dump())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient


@router.get("/patients", response_model=List[PatientResponse])
def list_patients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    patients = db.query(Patient).offset(skip).limit(limit).all()
    return patients


@router.get("/patients/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


# ============== DOCTOR ENDPOINTS ==============

@router.post("/doctors", response_model=DoctorResponse)
def create_doctor(doctor: DoctorCreate, db: Session = Depends(get_db)):
    db_doctor = Doctor(**doctor.model_dump())
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    return db_doctor


@router.get("/doctors", response_model=List[DoctorResponse])
def list_doctors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    doctors = db.query(Doctor).offset(skip).limit(limit).all()
    return doctors


@router.get("/doctors/{doctor_id}", response_model=DoctorResponse)
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor


@router.get("/doctors/license/{license_number}", response_model=DoctorResponse)
def get_doctor_by_license(license_number: str, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.license_number == license_number).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor


# ============== APPOINTMENT ENDPOINTS ==============

@router.post("/appointments", response_model=AppointmentResponse)
def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == appointment.patient_id).first()
    if not patient:
        raise HTTPException(status_code=400, detail="Referenced patient does not exist")
        
    # Verify doctor exists
    doctor = db.query(Doctor).filter(Doctor.id == appointment.doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=400, detail="Referenced doctor does not exist")

    db_appointment = Appointment(**appointment.model_dump())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment


@router.get("/appointments", response_model=List[AppointmentResponse])
def list_appointments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    appointments = db.query(Appointment).offset(skip).limit(limit).all()
    return appointments


@router.get("/appointments/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment


@router.put("/appointments/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(appointment_id: int, update: AppointmentUpdate, db: Session = Depends(get_db)):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(appointment, field, value)
    
    db.commit()
    db.refresh(appointment)
    return appointment


# ============== VACCINATION ENDPOINTS ==============

@router.post("/vaccinations", response_model=VaccinationResponse)
def create_vaccination(vaccination: VaccinationCreate, db: Session = Depends(get_db)):
    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == vaccination.patient_id).first()
    if not patient:
        raise HTTPException(status_code=400, detail="Referenced patient does not exist")

    db_vaccination = Vaccination(**vaccination.model_dump())
    db.add(db_vaccination)
    db.commit()
    db.refresh(db_vaccination)
    return db_vaccination


@router.get("/vaccinations/patient/{patient_id}", response_model=List[VaccinationResponse])
def list_patient_vaccinations(patient_id: int, db: Session = Depends(get_db)):
    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
        
    vaccinations = db.query(Vaccination).filter(Vaccination.patient_id == patient_id).all()
    return vaccinations


@router.post("/vaccinations/{vaccination_id}/administer", response_model=VaccinationResponse)
def administer_vaccination(vaccination_id: int, admin: VaccinationAdminister, db: Session = Depends(get_db)):
    vaccination = db.query(Vaccination).filter(Vaccination.id == vaccination_id).first()
    if not vaccination:
        raise HTTPException(status_code=404, detail="Vaccination record not found")
    
    vaccination.administered_date = admin.administered_date
    vaccination.batch_number = admin.batch_number or vaccination.batch_number
    vaccination.location = admin.location or vaccination.location
    vaccination.status = "administered"
    
    db.commit()
    db.refresh(vaccination)
    return vaccination


# ============== CONTRACEPTIVE ENDPOINTS ==============

@router.post("/contraceptives", response_model=ContraceptiveResponse)
def create_contraceptive(contraceptive: ContraceptiveCreate, offline: bool = False, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == contraceptive.patient_id).first()
    if not patient:
        raise HTTPException(status_code=400, detail="Referenced patient does not exist")

    zk_service = get_zk_service()

    if patient.date_of_birth:
        dob_year = patient.date_of_birth.year
        current_year = datetime.now().year
        min_age = 18
        proof = zk_service.generate_age_proof(dob_year, current_year, min_age)
        is_eligible = proof["age_verified"]
    else:
        is_eligible = True
        proof = {"proof_hash": "no_dob_provided", "public_signals": {"is_eligible": 1}}

    signals = proof.get("public_signals", {})
    if "circuit" not in signals:
        signals["circuit"] = "age_check"

    notes = contraceptive.notes or ""
    if is_eligible:
        notes += f"\n[ZK Verified: Patient eligibility confirmed. Verification Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]"

    db_contraceptive = ContraceptiveRecord(
        **contraceptive.model_dump(),
        prescription_date=datetime.now(),
        notes=notes.strip()
    )
    db.add(db_contraceptive)
    db.commit()
    db.refresh(db_contraceptive)

    queue_item = StellarSyncQueue(
        entity_type="contraceptive_eligibility",
        entity_id=db_contraceptive.id,
        proof_hash=proof["proof_hash"],
        public_signals=signals,
        status="pending"
    )
    db.add(queue_item)
    db.commit()

    if not offline:
        try:
            sync_res = zk_service.submit_to_stellar(proof["proof_hash"], signals)
            if sync_res.get("success"):
                queue_item.status = "synced"
                queue_item.tx_hash = sync_res.get("tx_hash")
                queue_item.synced_at = datetime.now()
                db.commit()
        except (ProofError, Exception) as e:
            queue_item.status = "failed"
            queue_item.error_message = str(e)
            db.commit()

    return db_contraceptive


@router.get("/contraceptives/patient/{patient_id}", response_model=List[ContraceptiveResponse])
def list_patient_contraceptives(patient_id: int, db: Session = Depends(get_db)):
    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    records = db.query(ContraceptiveRecord).filter(
        ContraceptiveRecord.patient_id == patient_id
    ).all()
    return records


# ============== DOCTOR VERIFICATION ENDPOINTS ==============

@router.post("/verifications", response_model=DoctorVerificationResponse)
def create_verification(verification: DoctorVerificationCreate, offline: bool = False, db: Session = Depends(get_db)):
    zk_service = get_zk_service()

    doctor = db.query(Doctor).filter(Doctor.id == verification.doctor_id).first()
    if not doctor or not doctor.license_number:
        raise HTTPException(status_code=404, detail="Doctor or license not found")

    # Step 1: Check HPCSA registration
    hpcsa_result = zk_service.check_hpcsa(
        license_number=doctor.license_number,
        surname=doctor.last_name or "",
        first_name=doctor.first_name or "",
    )

    # For demo: proceed with ZK even if HPCSA not found (mock fallback)
    if not hpcsa_result.get("found") and hpcsa_result.get("source") == "hpcsa_live":
        raise HTTPException(
            status_code=400,
            detail=f"Doctor not found on HPCSA iRegister: {hpcsa_result.get('error', 'Unknown error')}",
        )

    # Step 2: Generate ZK proof
    proof = zk_service.generate_license_proof(doctor.license_number, verification.doctor_id)
    proof_hash = proof["proof_hash"]
    initial_status = "pending" if offline else "verified"

    signals = proof["public_signals"]
    signals["circuit"] = "license_verify"

    verification_data = verification.model_dump()
    verification_data.pop("credential_data", None)

    db_verification = DoctorVerification(
        **verification_data,
        status=initial_status,
        verification_date=datetime.now(),
        credential_hash=proof["credential_hash"],
        zk_proof_hash=proof_hash,
        public_signals=signals,
        hpcsa_status=hpcsa_result.get("status"),
        hpcsa_checked_at=datetime.now(),
        hpcsa_full_name=hpcsa_result.get("full_name"),
        hpcsa_register=hpcsa_result.get("register"),
    )
    db.add(db_verification)
    db.commit()
    db.refresh(db_verification)

    queue_item = StellarSyncQueue(
        entity_type="doctor_verification",
        entity_id=db_verification.id,
        proof_hash=proof_hash,
        public_signals=signals,
        status="pending"
    )
    db.add(queue_item)
    db.commit()

    if not offline:
        try:
            sync_res = zk_service.submit_to_stellar(proof_hash, signals)
            if sync_res.get("success"):
                queue_item.status = "synced"
                queue_item.tx_hash = sync_res.get("tx_hash")
                queue_item.synced_at = datetime.now()
                db_verification.status = "verified"
                db.commit()
        except (ProofError, Exception) as e:
            queue_item.status = "failed"
            queue_item.error_message = str(e)
            db.commit()

    return db_verification


@router.get("/verifications/doctor/{doctor_id}", response_model=List[DoctorVerificationResponse])
def list_doctor_verifications(doctor_id: int, db: Session = Depends(get_db)):
    # Verify doctor exists
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    verifications = db.query(DoctorVerification).filter(
        DoctorVerification.doctor_id == doctor_id
    ).all()
    return verifications


# ============== STELLAR SYNC QUEUE ENDPOINTS ==============

@router.get("/sync/queue", response_model=List[StellarSyncQueueResponse])
def get_sync_queue(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(StellarSyncQueue)
    if status:
        query = query.filter(StellarSyncQueue.status == status)
    return query.all()


@router.post("/sync/stellar", response_model=List[StellarSyncQueueResponse])
def sync_to_stellar(db: Session = Depends(get_db)):
    pending_items = db.query(StellarSyncQueue).filter(StellarSyncQueue.status == "pending").all()
    zk_service = get_zk_service()

    for item in pending_items:
        try:
            signals = item.public_signals or {}
            if "circuit" not in signals:
                circuit_map = {
                    "doctor_verification": "license_verify",
                    "contraceptive_eligibility": "age_check",
                }
                signals["circuit"] = circuit_map.get(item.entity_type, "age_check")
            sync_res = zk_service.submit_to_stellar(
                proof_hash=item.proof_hash,
                public_signals=signals,
            )
            if sync_res.get("success"):
                item.status = "synced"
                item.tx_hash = sync_res.get("tx_hash")
                item.synced_at = datetime.now()

                if item.entity_type == "doctor_verification":
                    dv = db.query(DoctorVerification).filter(DoctorVerification.id == item.entity_id).first()
                    if dv:
                        dv.status = "verified"
            else:
                item.status = "failed"
                item.error_message = sync_res.get("error") or "Soroban verification call failed"
        except (ProofError, Exception) as e:
            item.status = "failed"
            item.error_message = str(e)

    db.commit()
    for item in pending_items:
        db.refresh(item)
    return pending_items