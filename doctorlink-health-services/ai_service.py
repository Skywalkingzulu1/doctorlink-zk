"""DoctorLink AI Service — OpenRouter integration for clinic finder & patient triage."""

import json
import os
from typing import Optional, List, Dict

import httpx

OPENROUTER_BASE = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "google/gemini-2.5-flash-lite"
DEFAULT_MAX_TOKENS = 512

SYSTEM_PROMPTS = {
    "clinic_finder": (
        "You are Dr. Link, a helpful clinic finder assistant for DoctorLink, a South African telemedicine platform. "
        "Given a patient's location and medical need, suggest the nearest appropriate clinic or healthcare facility. "
        "Ask clarifying questions if location or symptoms are vague. "
        "Always remind the patient to verify clinic hours before visiting. "
        "Do NOT give medical diagnoses — only suggest where to seek care. "
        "You have access to a database of real SA clinics. "
        "When the system provides clinic data alongside your response, briefly introduce the best match. "
        "Keep your answer to 1-2 sentences. "
        "Be warm and proactive: offer to check availability, provide directions, or give the phone number."
    ),
    "triage": (
        "You are Dr. Link, a patient intake triage assistant for DoctorLink. "
        "Ask the patient one key question at a time about their symptoms. "
        "Based on their answers, suggest an appropriate care level: self-care, clinic visit, or emergency. "
        "Always err on the side of caution and recommend professional care for anything serious. "
        "Be concise — one question per turn."
    ),
    "general": (
        "You are Dr. Link, a helpful assistant for DoctorLink, a South African healthcare platform. "
        "Answer questions about the platform, ZK health compliance, and general health information. "
        "Do NOT provide medical diagnoses. Direct patients to a doctor for medical advice. "
        "Be concise (max 3 sentences)."
    ),
}


class AIService:
    def __init__(self, api_key: str, model: str = DEFAULT_MODEL):
        self.api_key = api_key
        self.model = model
        self.client = httpx.Client(timeout=30)

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def chat(self, messages: List[Dict], system_prompt: str = "general",
             max_tokens: int = DEFAULT_MAX_TOKENS) -> Dict:
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPTS.get(system_prompt, SYSTEM_PROMPTS["general"])},
                *messages,
            ],
            "max_tokens": max_tokens,
        }
        try:
            resp = self.client.post(
                f"{OPENROUTER_BASE}/chat/completions",
                headers=self._headers(),
                json=body,
            )
            resp.raise_for_status()
            data = resp.json()
            choice = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            return {
                "ok": True,
                "reply": choice,
                "model": data.get("model", self.model),
                "tokens": usage.get("total_tokens", 0),
            }
        except httpx.HTTPStatusError as e:
            detail = ""
            try:
                detail = e.response.text[:300]
            except Exception:
                detail = str(e)
            return {"ok": False, "error": f"HTTP {e.response.status_code}: {detail}"}
        except Exception as e:
            return {"ok": False, "error": str(e)[:300]}

    def clinic_finder(self, messages: List[Dict]) -> Dict:
        from clinic_service import get_clinic_service
        cs = get_clinic_service()

        last_message = messages[-1]["content"] if messages else ""
        matched = cs.search_by_location(last_message)
        if not matched:
            for m in messages:
                matched = cs.search_by_location(m.get("content", ""))
                if matched:
                    break

        clinic_data = matched[:3]
        if clinic_data:
            clinic_text = "\n".join(
                f"- {c['name']} ({c['city']}) — {c['phone']} | {c['address']}"
                for c in clinic_data
            )
            info_msg = (
                f"Here are clinics matching your request:\n{clinic_text}\n\n"
                "Briefly recommend the best option based on the user's needs."
            )
        else:
            info_msg = ""

        messages_with_data = messages.copy()
        if info_msg:
            messages_with_data.append({"role": "system", "content": info_msg})

        result = self.chat(messages_with_data, system_prompt="clinic_finder")
        result["clinics"] = clinic_data
        return result

    def triage(self, messages: List[Dict]) -> Dict:
        return self.chat(messages, system_prompt="triage")

    def close(self):
        self.client.close()


_instance: Optional[AIService] = None


def get_ai_service() -> AIService:
    global _instance
    if _instance is None:
        from config import settings
        _instance = AIService(
            api_key=settings.OPENROUTER_API_KEY,
            model=settings.OPENROUTER_MODEL or DEFAULT_MODEL,
        )
    return _instance
