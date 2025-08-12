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
                "sender": "T-Coop",
                "messagetext": f"{message}",
                "flash": "0",
            },
            "recipients": {
                "gsm": [{"msidn": f"234{phone_number[1::]}", "msgid": uuid4().hex}]
            },
        }
    }

    try:
        response = await client.post(url=url, json=data, timeout=None)
        if response.status_code >= 400:
            response.raise_for_status()
        LOGGER.info("OTP SENT")
        return True
    except Exception as e:
        LOGGER.error(f"OTP Failed to SEND:{message}, and expection info: {e}")

        return False
