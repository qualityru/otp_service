from fastapi import FastAPI

from api.otp.routes import router as otp_router

api_app = FastAPI(title="OTP API")

api_app.include_router(otp_router)
