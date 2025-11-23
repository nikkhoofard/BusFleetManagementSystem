import httpx
from typing import Optional
from app.core.config import settings


class SMSService:
    def __init__(self):
        self.api_key = settings.ippanel_api_key.strip()
        self.sender_number = settings.ippanel_sender_number
        self.base_url = "https://edge.ippanel.com/v1/api/send"
    
    async def send_verification_code(self, mobile: str, code: str) -> bool:
        try:
            # Convert 0910... → 98910...
            if mobile.startswith("0"):
                mobile = "98" + mobile[1:]

            payload = {
                "sending_type": "pattern",
                "from_number": self.sender_number,
                "code": "0s4osu9wi3ekzsv",
                "recipients": [mobile],  
                "params": {
                    "code": str(code)
                }
            }

            headers = {
                "Authorization": self.api_key,
                "Content-Type": "application/json",
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    json=payload,
                    headers=headers,
                    timeout=10,
                )

            print("STATUS:", response.status_code)
            print("BODY:", response.text)

            response.raise_for_status()
            return True

        except Exception as e:
            print(f"Error sending SMS: {e}")
            return False


sms_service = SMSService()

