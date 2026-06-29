"""DoctorLink Health Services - Pydantic schemas."""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, date
from typing import Optional, List
from enum import Enum


class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class VaccinationStatus(str, Enum):
    PENDING = "pending"
    ADMINISTERED = "administered"
    OVERDUE = "overdue"
    SKIPPED = "skipped"


class ContraceptiveStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"
    EXPIRED = "expired"


class DoctorVerificationStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"


# Patient schemas
class PatientBase(BaseModel):
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=50)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, max_length=20)


class PatientCreate(PatientBase):
    pass


class PatientResponse(PatientBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Doctor schemas
class DoctorBase(BaseModel):
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=50)
    license_number: Optional[str] = Field(None, max_length=100)
    specialization: Optional[str] = Field(None, max_length=100)


class DoctorCreate(DoctorBase):
    pass


class DoctorResponse(DoctorBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Appointment schemas
class AppointmentBase(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_datetime: datetime
    reason: Optional[str] = None
    duration_minutes: Optional[int] = 30


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentUpdate(BaseModel):
    status: Optional[AppointmentStatus] = None
    notes: Optional[str] = None


class AppointmentResponse(AppointmentBase):
    id: int
    status: AppointmentStatus
    notes: Optional[str] = None
    created_at: datetime
    patient: Optional[PatientResponse] = None
    doctor: Optional[DoctorResponse] = None

    class Config:
        from_attributes = True


# Vaccination schemas
class VaccinationBase(BaseModel):
    patient_id: int
    vaccine_name: str = Field(..., max_length=255)
    dose_number: Optional[int] = None
    total_doses: Optional[int] = None
    next_due_date: Optional[date] = None
    batch_number: Optional[str] = None
    location: Optional[str] = None


class VaccinationCreate(VaccinationBase):
    administered_date: Optional[date] = None


class VaccinationAdminister(BaseModel):
    administered_date: date
    batch_number: Optional[str] = None
    location: Optional[str] = None


class VaccinationResponse(VaccinationBase):
    id: int
    administered_date: Optional[date] = None
    status: VaccinationStatus
    created_at: datetime

    class Config:
        from_attributes = True


# Contraceptive schemas
class ContraceptiveBase(BaseModel):
    patient_id: int
    contraceptive_type: str = Field(..., max_length=100)
    brand_name: Optional[str] = Field(None, max_length=100)
    prescribed_by: Optional[str] = None


class ContraceptiveCreate(ContraceptiveBase):
    start_date: date
    end_date: Optional[date] = None


class ContraceptiveUpdate(BaseModel):
    status: Optional[ContraceptiveStatus] = None
    end_date: Optional[date] = None
    notes: Optional[str] = None


class ContraceptiveResponse(ContraceptiveBase):
    id: int
    start_date: date
    end_date: Optional[date] = None
    status: ContraceptiveStatus
    prescription_date: Optional[date] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Doctor Verification schemas
class DoctorVerificationBase(BaseModel):
    doctor_id: int
    verification_type: str = Field(..., max_length=50)
    provider: Optional[str] = Field(None, max_length=100)


class DoctorVerificationCreate(DoctorVerificationBase):
    credential_data: str


class DoctorVerificationResponse(DoctorVerificationBase):
    id: int
    status: DoctorVerificationStatus
    verification_date: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    zk_proof_hash: Optional[str] = None
    created_at: datetime
    hpcsa_status: Optional[str] = None
    hpcsa_checked_at: Optional[datetime] = None
    hpcsa_full_name: Optional[str] = None
    hpcsa_register: Optional[str] = None

    class Config:
        from_attributes = True


# ZK Proof verification
class ZKProofVerify(BaseModel):
    proof: str
    public_signals: dict


class StellarSyncQueueResponse(BaseModel):
    id: int
    entity_type: str
    entity_id: int
    proof_hash: str
    public_signals: Optional[dict] = None
    status: str
    error_message: Optional[str] = None
    tx_hash: Optional[str] = None
    created_at: datetime
    synced_at: Optional[datetime] = None

    class Config:
        from_attributes = True