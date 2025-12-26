import asyncio
import random
import re
from email.mime.text import MIMEText
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

import aiohttp

from aiosmtplib import SMTP
from loguru import logger

from config import settings


class WhatsAppRetryableError(Exception):
    pass


class OTPCode:
    smtp_server = "smtp.gmail.com"
    smtp_port = 465
    from_email = settings.SMTP_LOGIN
    from_password = settings.SMTP_PASSWORD
    code_length = int(settings.CODE_LENGHT)

    @classmethod
    async def send(cls, type_, user_login, **kwargs):
        min_val = 10**(cls.code_length - 1)
        max_val = (10**cls.code_length) - 1

        code = str(random.randint(min_val, max_val))
        send_func = getattr(cls, f"send_by_{type_}")
        asyncio.create_task(send_func(user_login, code, **kwargs))
        return int(code)

    @classmethod
    @retry(
        stop=stop_after_attempt(10),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(WhatsAppRetryableError),
        reraise=True,
    )
    async def send_by_whatsapp(
        cls, phone_number, code, change_password=None, lang="en_US", **kwargs
    ):
        phone_number = re.sub(r"\D", "", phone_number)
        template_name = (
            settings.OPT_CHANGE_PASSWORD_TEMPLATE
            if change_password
            else settings.OTP_TEMPLATE
        )
        url = f"https://graph.facebook.com/v22.0/{settings.WHATSAPP_NUMBER_ID}/messages"

        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": lang},
                "components": [
                    {
                        "type": "body",
                        "parameters": [{"type": "text", "text": str(code)}]
                    },
                    {
                        "type": "button",
                        "sub_type": "url",
                        "index": "0",
                        "parameters": [{"type": "text", "text": str(code)}]
                    }
                ]
            }
        }

        headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "curl/8.14.1"
        }

        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    resp_json = await response.json()

                    if response.status >= 400:
                        error_data = resp_json.get("error", {})

                        logger.error(
                            f"WhatsApp API Error {response.status}: {resp_json}"
                        )

                        if response.status >= 500 or response.status == 429:
                            raise WhatsAppRetryableError(
                                f"Temporary server error: {response.status}"
                            )

                        raise Exception(
                            f"WhatsApp permanent failure: {error_data.get('message')}"
                        )

                    logger.info(f"WhatsApp OTP sent successfully to {phone_number}!")
                    return resp_json

        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logger.warning(f"Connection error, retrying... Details: {e}")
            raise WhatsAppRetryableError(f"Network issue: {e}")

    @classmethod
    async def send_by_email(cls, to_email, code, **kwargs):
        text = f"<div><b>{code}</b></div>"
        message = MIMEText(text, "html")
        message["From"] = cls.from_email
        message["To"] = to_email
        message["Subject"] = "Your confirmation code"
        try:
            async with SMTP(
                hostname=cls.smtp_server, port=cls.smtp_port, use_tls=True
            ) as server:
                # await smtp.starttls()
                await server.login(cls.from_email, cls.from_password)
                await server.send_message(message)
                logger.info("Email sent successfully!")
                return code
        except Exception as e:
            logger.error(f"Failed to send email: {e}")


if __name__ == "__main__":
    asyncio.run(OTPCode.send("email", "email@gmail.com"))