import httpx
from typing import Optional
from app.core.config import settings


class SMSService:
    def __init__(self):
        self.api_key = settings.ippanel_api_key
        self.sender_number = settings.ippanel_sender_number
        self.base_url = "https://api2.ippanel.com/api/v1"
    
    async def send_verification_code(self, mobile: str, code: str) -> bool:
        """Send verification code via ippanel"""
        try:
            url = f"{self.base_url}/sms/send/simple"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "sender": self.sender_number or "50004001",
                "recipient": mobile,
                "message": f"کد تایید شما: {code}\nاین کد 5 دقیقه اعتبار دارد."
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers, timeout=10.0)
                response.raise_for_status()
                return True
        except Exception as e:
            print(f"Error sending SMS: {e}")
            return False


sms_service = SMSService()

