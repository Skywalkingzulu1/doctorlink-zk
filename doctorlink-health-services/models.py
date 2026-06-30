"""DoctorLink Health Services - Database models."""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum, ForeignKey, Date, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import hashlib
from datetime import datetime
import enum

Base = declarative_base()


class AppointmentStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class VaccinationStatus(str, enum.Enum):
    PENDING = "pending"
    ADMINISTERED = "administered"
    OVERDUE = "overdue"
    SKIPPED = "skipped"


class ContraceptiveStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"
    EXPIRED = "expired"


class DoctorVerificationStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(50))
    date_of_birth = Column(Date)
    gender = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)

    appointments = relationship("Appointment", back_populates="patient")
    vaccinations = relationship("Vaccination", back_populates="patient")
    contraceptives = relationship("ContraceptiveRecord", back_populates="patient")


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(50))
    license_number = Column(String(100), unique=True)
    specialization = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

    appointments = relationship("Appointment", back_populates="doctor")
    verifications = relationship("DoctorVerification", back_populates="doctor")


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    appointment_datetime = Column(DateTime, nullable=False)
    reason = Column(Text)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED)
    duration_minutes = Column(Integer, default=30)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")


class Vaccination(Base):
    __tablename__ = "vaccinations"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    vaccine_name = Column(String(255), nullable=False)
    dose_number = Column(Integer)
    total_doses = Column(Integer)
    administered_date = Column(Date)
    next_due_date = Column(Date)
    status = Column(Enum(VaccinationStatus), default=VaccinationStatus.PENDING)
    batch_number = Column(String(100))
    location = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="vaccinations")


class ContraceptiveRecord(Base):
    __tablename__ = "contraceptive_records"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    contraceptive_type = Column(String(100), nullable=False)
    brand_name = Column(String(100))
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(Enum(ContraceptiveStatus), default=ContraceptiveStatus.ACTIVE)
    prescribed_by = Column(String(100))
    prescription_date = Column(Date)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="contraceptives")


class DoctorVerification(Base):
    __tablename__ = "doctor_verifications"

    id = Column(Integer, primary_key=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    verification_type = Column(String(50), nullable=False)
    credential_hash = Column(String(255))
    status = Column(Enum(DoctorVerificationStatus), default=DoctorVerificationStatus.PENDING)
    provider = Column(String(100))
    verification_date = Column(DateTime)
    expires_at = Column(DateTime)
    zk_proof_hash = Column(String(255))
    public_signals = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    # HPCSA iRegister integration
    hpcsa_status = Column(String(50), nullable=True)     # Active, Erased, Suspended, Not Found
    hpcsa_checked_at = Column(DateTime, nullable=True)    # When HPCSA was last queried
    hpcsa_full_name = Column(String(255), nullable=True)  # Name returned by HPCSA
    hpcsa_register = Column(String(100), nullable=True)   # e.g. MEDICAL PRACTITIONER

    doctor = relationship("Doctor", back_populates="verifications")


class StellarSyncQueue(Base):
    __tablename__ = "stellar_sync_queue"

    id = Column(Integer, primary_key=True)
    entity_type = Column(String(50), nullable=False)  # "doctor_verification", "contraceptive_eligibility"
    entity_id = Column(Integer, nullable=False)
    proof_hash = Column(String(255), nullable=False)
    public_signals = Column(JSON)
    status = Column(String(20), default="pending")  # "pending", "synced", "failed"
    error_message = Column(Text, nullable=True)
    tx_hash = Column(String(66), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    synced_at = Column(DateTime, nullable=True)


from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def seed_db(session):
    # Check if empty
    if session.query(Patient).first() is not None or session.query(Doctor).first() is not None:
        return

    from datetime import date, timedelta
    
    # 1. Add Patients
    jane = Patient(
        first_name="Jane",
        last_name="Doe",
        email="jane.doe@example.com",
        phone="+1 (555) 019-2834",
        date_of_birth=date(1995, 5, 12),
        gender="female"
    )
    alice = Patient(
        first_name="Alice",
        last_name="Smith",
        email="alice.smith@example.com",
        phone="+1 (555) 014-9988",
        date_of_birth=date(1990, 8, 22),
        gender="female"
    )
    robert = Patient(
        first_name="Robert",
        last_name="Johnson",
        email="robert.j@example.com",
        phone="+1 (555) 012-3456",
        date_of_birth=date(1985, 2, 14),
        gender="male"
    )
    session.add_all([jane, alice, robert])
    session.flush() # Populate IDs

    # 2. Add Doctors
    # SA doctors with HPCSA-style registration numbers (demonstrate real format)
    thabo = Doctor(
        first_name="Thabo",
        last_name="Mokoena",
        email="dr.mokoena@doctorlink.co.za",
        phone="+27 82 555 0101",
        license_number="MP0456789",
        specialization="Family Medicine"
    )
    lindiwe = Doctor(
        first_name="Lindiwe",
        last_name="Nkosi",
        email="dr.nkosi@doctorlink.co.za",
        phone="+27 72 555 0202",
        license_number="MP0987654",
        specialization="Paediatrics"
    )
    # Demo/international doctors with fake license numbers
    sarah = Doctor(
        first_name="Sarah",
        last_name="Connor",
        email="dr.connor@doctorlink.com",
        phone="+1 (555) 018-7722",
        license_number="LIC-98765-MD",
        specialization="Family Medicine"
    )
    gregory = Doctor(
        first_name="Gregory",
        last_name="House",
        email="dr.house@doctorlink.com",
        phone="+1 (555) 011-5050",
        license_number="LIC-12345-MD",
        specialization="Infectious Diseases"
    )
    session.add_all([thabo, lindiwe, sarah, gregory])
    session.flush() # Populate IDs

    # 3. Add Appointments
    appt1 = Appointment(
        patient_id=jane.id,
        doctor_id=sarah.id,
        appointment_datetime=datetime.utcnow() + timedelta(days=1, hours=2),
        reason="Annual wellness exam and contraceptive review",
        status=AppointmentStatus.SCHEDULED,
        notes="Patient requested discussion about long-term contraceptive options."
    )
    appt2 = Appointment(
        patient_id=robert.id,
        doctor_id=gregory.id,
        appointment_datetime=datetime.utcnow() + timedelta(days=3, hours=4),
        reason="Follow-up on persistent joint pain and fatigue",
        status=AppointmentStatus.CONFIRMED,
        notes="Check inflammatory markers from recent lab results."
    )
    session.add_all([appt1, appt2])

    # 4. Add Vaccinations
    vac1 = Vaccination(
        patient_id=jane.id,
        vaccine_name="COVID-19 (Pfizer-BioNTech)",
        dose_number=1,
        total_doses=2,
        administered_date=date(2026, 1, 15),
        status=VaccinationStatus.ADMINISTERED,
        batch_number="PZ-88291",
        location="DoctorLink Central Clinic"
    )
    vac2 = Vaccination(
        patient_id=jane.id,
        vaccine_name="COVID-19 (Pfizer-BioNTech)",
        dose_number=2,
        total_doses=2,
        next_due_date=date(2026, 2, 15),
        status=VaccinationStatus.PENDING,
        batch_number=None,
        location=None
    )
    vac3 = Vaccination(
        patient_id=robert.id,
        vaccine_name="Influenza (Quadrivalent)",
        dose_number=1,
        total_doses=1,
        administered_date=date(2025, 11, 10),
        status=VaccinationStatus.ADMINISTERED,
        batch_number="FL-99021",
        location="Downtown Pharmacy"
    )
    session.add_all([vac1, vac2, vac3])

    # 5. Add Contraceptive Record
    contra = ContraceptiveRecord(
        patient_id=jane.id,
        contraceptive_type="Oral Contraceptive Pill",
        brand_name="Yasmin",
        start_date=date(2026, 2, 1),
        end_date=date(2027, 2, 1),
        status=ContraceptiveStatus.ACTIVE,
        prescribed_by="Dr. Sarah Connor",
        prescription_date=date(2026, 2, 1),
        notes="Take daily. Monitor blood pressure at next follow-up."
    )
    session.add(contra)

    # 6. Add Doctor Verification
    import json
    proof_input = json.dumps({"license": sarah.license_number, "id": sarah.id}, sort_keys=True)
    proof_hash = hashlib.sha256(proof_input.encode()).hexdigest()

    verification = DoctorVerification(
        doctor_id=sarah.id,
        verification_type="State Medical License",
        credential_hash=f"hash_{sarah.license_number}",
        status=DoctorVerificationStatus.VERIFIED,
        provider="State Medical Board",
        verification_date=datetime.utcnow() - timedelta(days=90),
        expires_at=datetime.utcnow() + timedelta(days=275),
        zk_proof_hash=proof_hash,
        public_signals={"license_hash": proof_hash}
    )
    session.add(verification)

    session.commit()


def init_db():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from config import settings
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    
    # Run seed
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        seed_db(session)
    finally:
        session.close()
        
    return engine


def get_db():
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import create_engine
    from config import settings
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()