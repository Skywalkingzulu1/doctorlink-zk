"""DoctorLink Clinic Service — Octoparse integration + seeded SA clinic data."""

import json
import os
from typing import Optional, List, Dict
from dataclasses import dataclass, asdict
import httpx


@dataclass
class Clinic:
    name: str
    provider: str  # Netcare, Mediclinic, Life, Government, Private
    branch: str
    address: str
    city: str
    province: str
    phone: str
    lat: float
    lng: float
    specialty: str  # General, Emergency, Maternity, Vaccination, Dental, etc.
    hours: str
    services: List[str]


SEED_CLINICS = [
    Clinic("Netcare Christiaan Barnard Memorial Hospital", "Netcare", "Cape Town CBD",
           "181 Longmarket Street", "Cape Town", "Western Cape", "+27 21 480 6111",
           -33.9261, 18.4223, "General",
           "24/7 Emergency", ["Emergency", "General Surgery", "Cardiology", "Maternity"]),
    Clinic("Netcare Milpark Hospital", "Netcare", "Parktown",
           "9 Guild Road", "Johannesburg", "Gauteng", "+27 11 480 5600",
           -26.1804, 28.0238, "General",
           "24/7 Emergency", ["Emergency", "Oncology", "Cardiology", "Neurosurgery"]),
    Clinic("Netcare Sunninghill Hospital", "Netcare", "Sunninghill",
           "Cnr Nanyuki & Witkoppen Road", "Johannesburg", "Gauteng", "+27 11 806 1500",
           -26.0334, 28.0691, "General",
           "24/7 Emergency", ["Emergency", "Paediatrics", "Maternity", "Orthopaedics"]),
    Clinic("Netcare Umlazi Hospital", "Netcare", "Umlazi",
           "Vusi Mzemela Road", "Durban", "KwaZulu-Natal", "+27 31 907 8000",
           -29.9655, 30.8765, "General",
           "24/7 Emergency", ["Emergency", "Maternity", "Paediatrics"]),
    Clinic("Netcare Blaauwberg Hospital", "Netcare", "Blouberg",
           "Blaauwberg Road", "Cape Town", "Western Cape", "+27 21 554 0000",
           -33.8082, 18.5123, "General",
           "24/7 Emergency", ["Emergency", "Maternity", "General Surgery"]),

    Clinic("Mediclinic Cape Town", "Mediclinic", "Cape Town CBD",
           "21 Hof Street", "Cape Town", "Western Cape", "+27 21 423 3100",
           -33.9276, 18.4155, "General",
           "24/7 Emergency", ["Emergency", "Cardiology", "Neurology", "Maternity"]),
    Clinic("Mediclinic Morningside", "Mediclinic", "Morningside",
           "Cnr Rivonia & Grosvenor Road", "Johannesburg", "Gauteng", "+27 11 650 2000",
           -26.0991, 28.0616, "General",
           "24/7 Emergency", ["Emergency", "Cardiology", "Maternity", "Orthopaedics"]),
    Clinic("Mediclinic Pietermaritzburg", "Mediclinic", "Pietermaritzburg",
           "90 Miller Street", "Pietermaritzburg", "KwaZulu-Natal", "+27 33 845 2000",
           -29.6117, 30.3765, "General",
           "24/7 Emergency", ["Emergency", "Maternity", "General Surgery", "Paediatrics"]),
    Clinic("Mediclinic Louis Leipoldt", "Mediclinic", "Belhar",
           "Cnr Kipling & De La Bat Street", "Cape Town", "Western Cape", "+27 21 951 5111",
           -33.9384, 18.6186, "General",
           "24/7 Emergency", ["Emergency", "Maternity", "Paediatrics"]),

    Clinic("Life Hospital Chris Hani Baragwanath", "Life Healthcare", "Soweto",
           "Chris Hani Road", "Soweto", "Gauteng", "+27 11 933 8000",
           -26.2474, 27.9519, "General",
           "24/7 Emergency", ["Emergency", "Maternity", "Paediatrics", "Trauma"]),
    Clinic("Life Kingsbury Hospital", "Life Healthcare", "Claremont",
           "Wilderness Road", "Cape Town", "Western Cape", "+27 21 670 4000",
           -33.9781, 18.4669, "General",
           "24/7 Emergency", ["Emergency", "Cardiology", "Maternity", "Oncology"]),
    Clinic("Life Entabeni Hospital", "Life Healthcare", "Durban",
           "148 South Ridge Road", "Durban", "KwaZulu-Natal", "+27 31 204 1300",
           -29.8549, 31.0002, "General",
           "24/7 Emergency", ["Emergency", "Cardiology", "Neurosurgery", "Maternity"]),
    Clinic("Life Wilgeheuwel Hospital", "Life Healthcare", "Roodepoort",
           "Cnr Christiaan De Wet Rd & Prosperity Ave", "Johannesburg", "Gauteng", "+27 11 768 1111",
           -26.1206, 27.9107, "General",
           "24/7 Emergency", ["Emergency", "Maternity", "Paediatrics", "General Surgery"]),

    Clinic("Soweto Community Clinic", "Government", "Soweto",
           "2156 Chris Hani Road, Orlando West", "Soweto", "Gauteng", "+27 11 527 7500",
           -26.2543, 27.9192, "General",
           "Mon-Fri 7:00-18:00", ["Primary Care", "Vaccination", "HIV/AIDS", "TB Treatment"]),
    Clinic("Khayelitsha Community Health Centre", "Government", "Khayelitsha",
           "Steve Biko Road, Site B", "Cape Town", "Western Cape", "+27 21 360 4600",
           -34.0346, 18.6758, "General",
           "Mon-Fri 7:00-17:00", ["Primary Care", "Maternity", "Vaccination", "HIV/AIDS"]),
    Clinic("Clareinch Clinic", "Government", "Claremont",
           "St Thomas Road", "Cape Town", "Western Cape", "+27 21 671 1854",
           -33.9787, 18.4663, "Primary Care",
           "Mon-Fri 8:00-16:00", ["Primary Care", "Vaccination", "Family Planning"]),

    Clinic("Cape Town Medicentre", "Private", "Cape Town CBD",
           "Bree Street, Cape Town", "Cape Town", "Western Cape", "+27 21 422 0200",
           -33.9207, 18.4218, "General",
           "Mon-Fri 8:00-18:00, Sat 8:00-13:00", ["GP Services", "Vaccination", "Travel Health"]),
    Clinic("Rosecare Clinic Rosebank", "Private", "Rosebank",
           "Keyes Avenue, Rosebank", "Johannesburg", "Gauteng", "+27 11 447 8900",
           -26.1448, 28.0438, "General",
           "Mon-Fri 7:00-19:00, Sat 8:00-14:00", ["GP Services", "Vaccination", "Wellness"]),
    Clinic("Durban Medical Centre", "Private", "Durban CBD",
           "Smith Street, Durban", "Durban", "KwaZulu-Natal", "+27 31 332 2030",
           -29.8603, 31.0295, "General",
           "Mon-Fri 8:00-17:00, Sat 8:00-12:00", ["GP Services", "Minor Surgery", "Vaccination"]),
    Clinic("Tshwane District Hospital", "Government", "Pretoria",
           "Dr Savage Road, Pretoria West", "Pretoria", "Gauteng", "+27 12 380 1000",
           -25.7459, 28.1850, "General",
           "24/7 Emergency", ["Emergency", "Maternity", "Paediatrics", "General Surgery"]),
]

OCTOPARSE_API_BASE = "https://openapi.octoparse.com"


class OctoparseClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.Client(timeout=15)

    def _headers(self):
        return {"x-api-key": self.api_key, "Content-Type": "application/json"}

    def get_task_groups(self) -> List[Dict]:
        try:
            r = self.client.get(f"{OCTOPARSE_API_BASE}/taskGroup", headers=self._headers())
            r.raise_for_status()
            return r.json().get("data", [])
        except Exception:
            return []

    def search_tasks(self, group_id: int) -> List[Dict]:
        try:
            r = self.client.get(
                f"{OCTOPARSE_API_BASE}/task/search?taskGroupId={group_id}",
                headers=self._headers(),
            )
            r.raise_for_status()
            return r.json().get("data", [])
        except Exception:
            return []

    def get_data(self, task_id: str) -> List[Dict]:
        try:
            r = self.client.get(
                f"{OCTOPARSE_API_BASE}/data/offset?taskId={task_id}&offset=0&count=100",
                headers=self._headers(),
            )
            r.raise_for_status()
            return r.json().get("data", [])
        except Exception:
            return []

    def close(self):
        self.client.close()


class ClinicService:
    def __init__(self, octoparse_api_key: str = ""):
        self.octo = OctoparseClient(octoparse_api_key) if octoparse_api_key else None
        self.clinics = SEED_CLINICS

    def search_by_location(self, query: str, limit: int = 5) -> List[Dict]:
        query = query.lower().strip()
        keywords = query.split()

        def score(c: Clinic) -> int:
            s = 0
            for kw in keywords:
                if kw in c.city.lower() or kw in c.province.lower():
                    s += 3
                if kw in c.name.lower():
                    s += 2
                if kw in c.branch.lower() or kw in c.address.lower():
                    s += 1
                for svc in c.services:
                    if kw in svc.lower() or kw in c.specialty.lower():
                        s += 1
            return s

        scored = [(score(c), c) for c in self.clinics]
        scored.sort(key=lambda x: -x[0])
        return [asdict(c) for s, c in scored if s > 0][:limit]

    def search_by_specialty(self, specialty: str, city: str = "") -> List[Dict]:
        specialty = specialty.lower()
        city = city.lower()
        results = []
        for c in self.clinics:
            svc_match = specialty in c.specialty.lower() or any(specialty in s.lower() for s in c.services)
            if svc_match and (not city or city in c.city.lower() or city in c.province.lower()):
                results.append(asdict(c))
        return results

    def all_clinics(self) -> List[Dict]:
        return [asdict(c) for c in self.clinics]

    def get_clinic(self, name: str) -> Optional[Dict]:
        for c in self.clinics:
            if c.name.lower() == name.lower():
                return asdict(c)
        return None

    def get_octoparse_status(self) -> Dict:
        if not self.octo:
            return {"connected": False, "reason": "No API key configured"}
        groups = self.octo.get_task_groups()
        if not groups:
            return {"connected": False, "reason": "No task groups found"}
        return {"connected": True, "groups": groups, "task_count": sum(
            len(self.octo.search_tasks(g["taskGroupId"])) for g in groups
        )}


_instance: Optional[ClinicService] = None


def get_clinic_service() -> ClinicService:
    global _instance
    if _instance is None:
        from config import settings
        _instance = ClinicService(
            octoparse_api_key=settings.OCTOPARSE_API_KEY or "",
        )
    return _instance
