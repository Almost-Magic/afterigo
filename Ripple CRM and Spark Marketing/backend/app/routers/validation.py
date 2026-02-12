"""Ripple CRM — Validation utility endpoint."""
import re
from fastapi import APIRouter

router = APIRouter(prefix="/validate", tags=["validation"])

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
PHONE_REGEX = re.compile(r"^[\d\s\-\+\(\)]{7,20}$")


@router.post("")
async def validate_fields(data: dict):
    """Validate a set of field values. Returns per-field errors."""
    errors = {}
    if "email" in data and data["email"]:
        if not EMAIL_REGEX.match(data["email"]):
            errors["email"] = "Invalid email format"
    if "phone" in data and data["phone"]:
        if not PHONE_REGEX.match(data["phone"]):
            errors["phone"] = "Invalid phone format (7-20 digits, spaces, dashes allowed)"
    if "first_name" in data and not (data.get("first_name") or "").strip():
        errors["first_name"] = "First name is required"
    if "last_name" in data and not (data.get("last_name") or "").strip():
        errors["last_name"] = "Last name is required"
    return {"valid": len(errors) == 0, "errors": errors}
