from pydantic import BaseModel, EmailStr, field_validator, ValidationInfo, TypeAdapter
from typing import Literal
import phonenumbers
import re


class SendOtpRequest(BaseModel):
    provider: Literal["email", "whatsapp"]
    target: str

    @field_validator("target")
    @classmethod
    def validate_target(cls, v: str, info: ValidationInfo):
        provider = info.data.get("provider")

        if not provider:
            return v

        if provider == "email":
            try:
                ta = TypeAdapter(EmailStr)
                ta.validate_python(v)
            except Exception:
                raise ValueError("Invalid email format")

        elif provider == "whatsapp":
            try:
                cleaned_v = re.sub(r"[^\d+]", "", v)
                num = phonenumbers.parse(cleaned_v, None)
                if not phonenumbers.is_valid_number(num):
                    raise ValueError()
            except Exception:
                raise ValueError(
                    "Incorrect phone number (use international format)"
                )

        return v


class SendOtpResponse(BaseModel):
    status: Literal["ok", "error"]
    detail: str | None = None
