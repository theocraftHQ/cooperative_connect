import logging
from uuid import uuid4

from httpx import AsyncClient

from theocraft_coop.root.settings import settings

LOGGER = logging.getLogger(name="__file__")


async def send_sms(message: str, phone_number: str):

    client = AsyncClient()

    url = settings.sms_url

    data = {
        "SMS": {
            "auth": {"username": settings.sms_username, "apikey": settings.sms_apikey},
            "message": {
                "sender": settings.app_name,
                "messagetext": f"{message}",
                "flash": "0",
            },
            "recipients": {"gsm": [{"msidn": phone_number, "msgid": uuid4().hex}]},
            "dndsender": 1,
        }
    }
    try:

        response = await client.post(url=url, json=data)

        response.raise_for_status()
        LOGGER.info("OTP SENT")
        return True
    except Exception:
        LOGGER.error(f"OTP Failed to SEND:{message}")

        return False
