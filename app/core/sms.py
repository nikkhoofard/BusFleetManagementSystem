import httpx
from typing import Optional
from app.core.config import settings


class SMSService:
    def __init__(self):
        self.api_key = settings.ippanel_api_key
        self.sender_number = settings.ippanel_sender_number
        self.base_url = "https://edge.ippanel.com/v1/api/send"
    
    async def send_verification_code(self, mobile: str, code: str) -> bool:
        print(f"Sending verification code to {mobile} with code {code} and api key {self.api_key}, sender number {self.sender_number}")
        """Send verification code via ippanel"""
        try:
            url = self.base_url
            # Convert mobile from e.g. 09103799860 to +989103799860
            if mobile.startswith('0'):
                mobile = '+98' + mobile[1:]
            headers = {
                "Authorization":str(self.api_key),
                "Content-Type": "application/json"
            }
            payload = {
                "sending_type": "pattern",
                "from_number": self.sender_number,
                "code": "0s4osu9wi3ekzsv",
                "recipient": [str(mobile)],
                "params": {
                    "code":str(code)
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers, timeout=10.0)

                response.raise_for_status()
                return True
        except Exception as e:
            print(f"Error sending SMS: {e}")
            return False


sms_service = SMSService()

