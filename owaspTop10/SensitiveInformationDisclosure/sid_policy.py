from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class User:
    user_id: str
    role: str  # "applicant" or "manager"


def _read_jsonl(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []

    rows: list[dict] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _extract_candidate_name(row: Dict[str, Any]) -> str:
    first_name = str(row.get("first_name", "")).strip()
    last_name = str(row.get("last_name", "")).strip()
    full_name = f"{first_name} {last_name}".strip()
    if full_name:
        return full_name

    resume_content = str(row.get("resume_content", ""))
    for line in resume_content.splitlines():
        if line.lower().startswith("name:"):
            parsed_name = line.split(":", 1)[1].strip()
            if parsed_name:
                return parsed_name

    return str(row.get("candidate_id", "Unknown Candidate")).strip() or "Unknown Candidate"


def list_candidates(data_dir: str) -> list[Dict[str, str]]:
    applicants_path = os.path.join(data_dir, "applicants.jsonl")
    applicants = _read_jsonl(applicants_path)

    results: list[Dict[str, str]] = []

    for row in applicants:
        candidate_id = str(row.get("candidate_id", "")).strip()
        owner_id = str(row.get("owner_id", "")).strip()
        candidate_name = _extract_candidate_name(row)

        if candidate_id:
            results.append(
                {
                    "candidate_id": candidate_id,
                    "owner_id": owner_id,
                    "candidate_name": candidate_name,
                    "label": f"{candidate_name} ({candidate_id})",
                }
            )

    return results


def list_demo_actors(data_dir: str) -> list[Dict[str, str]]:
    applicants_path = os.path.join(data_dir, "applicants.jsonl")
    applicants = _read_jsonl(applicants_path)

    seen_user_ids: set[str] = set()
    actors: list[Dict[str, str]] = [
        {
            "user_id": "manager1",
            "role": "manager",
            "label": "Hiring Manager (Full Access)",
        }
    ]

    for row in applicants:
        owner_id = str(row.get("owner_id", "")).strip()
        candidate_id = str(row.get("candidate_id", "")).strip()
        candidate_name = _extract_candidate_name(row)

        if owner_id and owner_id not in seen_user_ids:
            actors.append(
                {
                    "user_id": owner_id,
                    "role": "applicant",
                    "candidate_id": candidate_id,
                    "label": f"{candidate_name} ({candidate_id}) - Applicant",
                }
            )
            seen_user_ids.add(owner_id)

    return actors


def load_candidate_bundle(data_dir: str, candidate_id: str) -> Optional[Dict[str, Any]]:
    applicants_path = os.path.join(data_dir, "applicants.jsonl")
    hr_path = os.path.join(data_dir, "hr_evals.jsonl")

    applicants = _read_jsonl(applicants_path)
    candidate = next((a for a in applicants if str(a.get("candidate_id")) == str(candidate_id)), None)
    if not candidate:
        return None

    hr_rows = _read_jsonl(hr_path)
    hr = next((h for h in hr_rows if str(h.get("candidate_id")) == str(candidate_id)), {})

    bundle = {
        "candidate_id": str(candidate.get("candidate_id", "")),
        "owner_id": str(candidate.get("owner_id", "")),
        "first_name": str(candidate.get("first_name", "")),
        "last_name": str(candidate.get("last_name", "")),
        "email": str(candidate.get("email", "")),
        "application_status": str(candidate.get("application_status", "")),
        "resume_content": candidate.get("resume_content", ""),
        "hr_notes_label": hr.get("hr_notes_label", ""),
        "hr_notes_text": hr.get("hr_notes_text", ""),
        "hr_score": hr.get("hr_score", ""),
    }
    return bundle


def load_candidate_bundle_for_user(data_dir: str, owner_id: str) -> Optional[Dict[str, Any]]:
    applicants_path = os.path.join(data_dir, "applicants.jsonl")
    applicants = _read_jsonl(applicants_path)

    candidate = next((a for a in applicants if str(a.get("owner_id")) == str(owner_id)), None)
    if not candidate:
        return None

    candidate_id = str(candidate.get("candidate_id", "")).strip()
    if not candidate_id:
        return None

    return load_candidate_bundle(data_dir, candidate_id)


def load_all_candidate_bundles(data_dir: str) -> list[Dict[str, Any]]:
    applicants_path = os.path.join(data_dir, "applicants.jsonl")
    applicants = _read_jsonl(applicants_path)

    bundles: list[Dict[str, Any]] = []
    for row in applicants:
        candidate_id = str(row.get("candidate_id", "")).strip()
        if not candidate_id:
            continue

        bundle = load_candidate_bundle(data_dir, candidate_id)
        if bundle:
            bundles.append(bundle)

    return bundles


def can_access_candidate(user: User, bundle: Dict[str, Any]) -> bool:
    if user.role == "manager":
        return True
    if user.role == "applicant":
        return str(bundle.get("owner_id")) == user.user_id
    return False


def filter_fields_for_llm(user: User, bundle: Dict[str, Any]) -> Dict[str, Any]:
    if user.role == "manager":
        return {
            "candidate_id": bundle["candidate_id"],
            "owner_id": bundle["owner_id"],
            "first_name": bundle["first_name"],
            "last_name": bundle["last_name"],
            "email": bundle["email"],
            "application_status": bundle["application_status"],
            "resume_content": bundle["resume_content"],
            "hr_notes_label": bundle["hr_notes_label"],
            "hr_notes_text": bundle["hr_notes_text"],
            "hr_score": bundle["hr_score"],
        }

    return {
        "candidate_id": bundle["candidate_id"],
        "owner_id": bundle["owner_id"],
        "first_name": bundle["first_name"],
        "last_name": bundle["last_name"],
        "email": bundle["email"],
        "application_status": bundle["application_status"],
        "resume_content": bundle["resume_content"],
    }


def format_context_text(context_obj: Dict[str, Any]) -> str:
    parts: list[str] = []

    if "candidate_id" in context_obj:
        parts.append(f"CANDIDATE ID: {context_obj.get('candidate_id', '')}")

    if "owner_id" in context_obj:
        parts.append(f"OWNER ID: {context_obj.get('owner_id', '')}")

    first_name = str(context_obj.get("first_name", "")).strip()
    last_name = str(context_obj.get("last_name", "")).strip()
    full_name = f"{first_name} {last_name}".strip()
    if full_name:
        parts.append(f"CANDIDATE NAME: {full_name}")

    email = str(context_obj.get("email", "")).strip()
    if email:
        parts.append(f"CANDIDATE EMAIL: {email}")

    application_status = str(context_obj.get("application_status", "")).strip()
    if application_status:
        parts.append(f"APPLICATION STATUS: {application_status}")

    resume = context_obj.get("resume_content", "")
    parts.append(f"CANDIDATE RESUME:\n{resume}".strip())

    if "hr_notes_label" in context_obj:
        parts.append(f"HR NOTES LABEL: {context_obj.get('hr_notes_label', '')}".strip())
        parts.append(f"HR NOTES TEXT:\n{context_obj.get('hr_notes_text', '')}".strip())
        parts.append(f"HR SCORE: {context_obj.get('hr_score', '')}".strip())

    return "\n\n".join(parts).strip()


def format_multiple_contexts(context_objects: list[Dict[str, Any]]) -> str:
    if not context_objects:
        return "No candidate records available."

    sections: list[str] = []
    for index, obj in enumerate(context_objects, start=1):
        sections.append(f"=== CANDIDATE RECORD {index} ===\n{format_context_text(obj)}")

    return "\n\n".join(sections).strip()