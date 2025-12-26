import pathlib

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = pathlib.Path(__file__).parent
ENV_PATH = BASE_DIR / "./.env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_PATH)

    CODE_LENGHT: str = Field("6", env="CODE_LENGHT")

    WHATSAPP_NUMBER_ID: str = Field(..., env="WHATSAPP_NUMBER_ID")
    WHATSAPP_TOKEN: str = Field(..., env="WHATSAPP_TOKEN")
    OTP_TEMPLATE: str = Field("only_otp_code", env="OTP_TEMPLATE")
    OPT_CHANGE_PASSWORD_TEMPLATE: str = Field(
        "change_password", env="OPT_CHANGE_PASSWORD_TEMPLATE"
    )

    SMTP_LOGIN: str = Field(..., env="SMTP_LOGIN")
    SMTP_PASSWORD: str = Field(..., env="SMTP_PASSWORD")


settings = Settings()
