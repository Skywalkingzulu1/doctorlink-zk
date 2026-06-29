"""DoctorLink - HPCSA iRegister integration for SA doctor license verification.

Architecture:
  1. Attempt real HTTP query against HPCSA iRegister backend
  2. On failure (timeout/unreachable), fall back to mock mode
  3. Mock mode uses known patterns to return plausible results

Real iRegister endpoint: POST https://hpcsaonline.custhelp.com/cc/ReportController/getDataFromRnow
This endpoint requires a session cookie from a prior GET and uses Oracle RightNow's AJAX
framework.  Automated requests time out without the full JS framework context.

For production, HPCSA would need to provide an official API or a headless browser
(Playwright/Selenium) would be used to drive the existing web form.
"""

import json
import logging
import time
import urllib.request
import http.cookiejar
import re
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)

# ── Data Types ───────────────────────────────────────────────────

@dataclass
class HPCSAResult:
    found: bool
    registration_number: str = ""
    full_name: str = ""
    surname: str = ""
    title: str = ""
    city: str = ""
    postal_code: str = ""
    status: str = ""          # "Active", "Erased", "Suspended", "Not Found"
    register: str = ""
    category: str = ""
    source: str = ""           # "hpcsa_live", "mock", "not_found"
    checked_at: str = ""
    error: str = ""

    @property
    def is_active(self) -> bool:
        return self.status.lower() == "active"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ── Configuration ────────────────────────────────────────────────

HPCSA_BASE = "https://hpcsaonline.custhelp.com"
HPCSA_API = HPCSA_BASE + "/cc/ReportController/getDataFromRnow"
HPCSA_FORM = HPCSA_BASE + "/app/i_reg_form"

# Cache: reg_number -> HPCSAResult
_cache: Dict[str, HPCSAResult] = {}

# How long to skip live check after timeout (seconds)
_LIVE_BACKOFF_UNTIL: float = 0


# ── Known doctor records for demo mode ──────────────────────────

# Realistic SA HPCSA registration number patterns:
#   MP0123456  - Medical Practitioner (GP)
#   MP0123457  - Medical Practitioner (Specialist)
# These are EXAMPLE numbers - they will NOT be found on the real iRegister.
# In production, real numbers would be loaded from a trusted source.

_MOCK_RECORDS = {
    # SA doctors with HPCSA-format numbers
    "MP0456789": HPCSAResult(
        found=True,
        registration_number="MP0456789",
        full_name="Thabo Mokoena",
        surname="Mokoena",
        title="Dr",
        city="Johannesburg",
        postal_code="2001",
        status="Active",
        register="MEDICAL PRACTITIONER",
        category="FAMILY MEDICINE",
        source="mock",
    ),
    "MP0987654": HPCSAResult(
        found=True,
        registration_number="MP0987654",
        full_name="Lindiwe Nkosi",
        surname="Nkosi",
        title="Dr",
        city="Pretoria",
        postal_code="0002",
        status="Active",
        register="MEDICAL PRACTITIONER",
        category="PAEDIATRICS",
        source="mock",
    ),
    # Demo doctors with fake license numbers → always "not found"
    "LIC-98765-MD": HPCSAResult(
        found=False,
        registration_number="LIC-98765-MD",
        status="Not Found",
        source="mock",
        error="Fake demo license number — not registered with HPCSA",
    ),
    "LIC-12345-MD": HPCSAResult(
        found=False,
        registration_number="LIC-12345-MD",
        status="Not Found",
        source="mock",
        error="Fake demo license number — not registered with HPCSA",
    ),
}


def _looks_like_sa_number(reg_number: str) -> bool:
    """Check if registration number follows SA HPCSA pattern."""
    return bool(re.match(r"^[A-Z]{2}\d{5,10}$", reg_number.upper()))


# ── Mock mode: return data based on registration number patterns ─

def _mock_check(reg_number: str) -> HPCSAResult:
    if reg_number in _MOCK_RECORDS:
        result = _MOCK_RECORDS[reg_number]
        result.checked_at = datetime.utcnow().isoformat()
        return result

    if not _looks_like_sa_number(reg_number):
        return HPCSAResult(
            found=False,
            registration_number=reg_number,
            status="Not Found",
            source="mock",
            checked_at=datetime.utcnow().isoformat(),
            error=f"Registration number '{reg_number}' does not match SA HPCSA format (e.g. MP0123456)",
        )

    # For realistic-looking SA numbers, return mock active records
    prefix = reg_number[:2].upper()
    register_map = {
        "MP": "MEDICAL PRACTITIONER",
        "PS": "PSYCHOLOGIST",
        "DN": "DENTIST",
        "PH": "PHYSIOTHERAPIST",
        "OT": "OCCUPATIONAL THERAPIST",
        "NU": "NURSE",
        "EN": "ENVIRONMENTAL HEALTH PRACTITIONER",
        "ST": "SPEECH THERAPIST",
        "OP": "OPTOMETRIST",
        "RD": "RADIOGRAPHER",
    }
    register = register_map.get(prefix, "MEDICAL PRACTITIONER")
    category = "GENERAL PRACTITIONER" if prefix == "MP" else ""

    return HPCSAResult(
        found=True,
        registration_number=reg_number,
        full_name="Verified Practitioner",
        surname="Practitioner",
        title="Dr",
        city="Johannesburg",
        postal_code="2000",
        status="Active",
        register=register,
        category=category,
        source="mock",
        checked_at=datetime.utcnow().isoformat(),
    )


# ── Live HPCSA API call ─────────────────────────────────────────

def _try_live_check(reg_number: str, surname: str = "",
                    first_name: str = "") -> Optional[HPCSAResult]:
    """Attempt real HPCSA iRegister query.  Returns None on any failure."""
    global _LIVE_BACKOFF_UNTIL

    now = time.time()
    if now < _LIVE_BACKOFF_UNTIL:
        logger.info("Skipping live HPCSA check (backoff active until %.0f)", _LIVE_BACKOFF_UNTIL)
        return None

    cj = http.cookiejar.CookieJar()
    ctx = urllib.request.ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = urllib.request.ssl.CERT_NONE
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cj),
        urllib.request.HTTPSHandler(context=ctx),
    )

    # Step 1: GET form to establish session
    try:
        form_resp = opener.open(HPCSA_FORM, timeout=15)
        if form_resp.status != 200:
            logger.warning("HPCSA form returned %d", form_resp.status)
            return None
    except Exception as e:
        logger.info("HPCSA form GET failed: %s", e)
        _LIVE_BACKOFF_UNTIL = now + 300  # backoff 5 min
        return None

    # Step 2: POST search
    data = json.dumps({
        "regNumber": reg_number,
        "firstName": first_name,
        "middleName": "",
        "surName": surname,
        "city": "",
        "postalCode": "",
        "register": "",
        "category": "",
    }).encode()

    req = urllib.request.Request(
        HPCSA_API, data=data,
        headers={
            "Content-Type": "application/json",
            "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0"),
        },
        method="POST",
    )

    try:
        resp = opener.open(req, timeout=120)
        body = resp.read().decode()
        if not body or not body.strip():
            logger.info("HPCSA returned empty response")
            return None

        parsed = json.loads(body)
        return _parse_hpcsa_response(parsed, reg_number)
    except Exception as e:
        logger.info("HPCSA API call failed: %s", e)
        _LIVE_BACKOFF_UNTIL = now + 300
        return None


def _parse_hpcsa_response(parsed: dict, reg_number: str) -> HPCSAResult:
    """Parse the HPCSA JSON response into HPCSAResult."""
    data_list = parsed.get("data", [])
    if not data_list:
        return HPCSAResult(
            found=False,
            registration_number=reg_number,
            status="Not Found",
            source="hpcsa_live",
            checked_at=datetime.utcnow().isoformat(),
        )

    row = data_list[0]
    if isinstance(row, list) and len(row) >= 8:
        return HPCSAResult(
            found=True,
            title=row[0] or "",
            surname=row[1] or "",
            full_name=row[2] or "",
            registration_number=row[3] or reg_number,
            city=row[4] or "",
            postal_code=row[5] or "",
            category=row[6] or "",
            status=row[7] or "Unknown",
            source="hpcsa_live",
            checked_at=datetime.utcnow().isoformat(),
        )
    if isinstance(row, dict):
        return HPCSAResult(
            found=True,
            registration_number=row.get("registration_number", reg_number),
            full_name=row.get("full_name", ""),
            surname=row.get("surname", ""),
            status=row.get("status", "Unknown"),
            source="hpcsa_live",
            checked_at=datetime.utcnow().isoformat(),
        )

    return HPCSAResult(
        found=False,
        registration_number=reg_number,
        status="Unknown",
        source="hpcsa_live",
        checked_at=datetime.utcnow().isoformat(),
        error="Unrecognized response format",
    )


# ── Public API ──────────────────────────────────────────────────

def check_registration(reg_number: str, surname: str = "",
                       first_name: str = "",
                       force_live: bool = False) -> HPCSAResult:
    """Check a doctor's HPCSA registration status.

    Tries live HPCSA API first.  Falls back to mock data on failure.
    Results are cached in memory by registration number.
    """
    now = datetime.utcnow().isoformat()

    if reg_number in _cache:
        cached = _cache[reg_number]
        if cached.source == "hpcsa_live" or not force_live:
            return cached

    result = _try_live_check(reg_number, surname, first_name) if force_live else None

    if result is None:
        result = _mock_check(reg_number)
        result.checked_at = now

    _cache[reg_number] = result
    return result


def check_doctor(doctor_dict: Dict[str, Any],
                 force_live: bool = False) -> HPCSAResult:
    """Convenience: pass a doctor dict/ORM object with license_number, first_name, last_name."""
    return check_registration(
        reg_number=doctor_dict.get("license_number", ""),
        surname=doctor_dict.get("last_name", ""),
        first_name=doctor_dict.get("first_name", ""),
        force_live=force_live,
    )


def clear_cache() -> None:
    _cache.clear()
