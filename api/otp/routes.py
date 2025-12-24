from fastapi import APIRouter
from .schemas import SendOtpResponse, SendOtpRequest
from .send_otp import OTPCode

router = APIRouter(prefix="/otp", tags=["otp"])


@router.post("/send", response_model=SendOtpResponse)
async def send_otp(data: SendOtpRequest):
    try:
        await OTPCode.send(data.provider, data.target)
    except Exception as exc:
        return SendOtpResponse(status="error", detail=str(exc))
    return SendOtpResponse(status="ok")
