import os
import logging
import requests
from dotenv import load_dotenv
from .base import SendResult

# Load env variables if not already loaded
load_dotenv()

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.api_key = os.getenv('RESEND_API_KEY')
        self.sender_email = os.getenv('DEFAULT_FROM_EMAIL')

    def send_email(self, recipient, subject, body):
        if not self.api_key or not self.sender_email:
            logger.error("Cannot send email: RESEND_API_KEY or DEFAULT_FROM_EMAIL missing in environment.")
            return SendResult(
                success=False,
                response={"provider": "resend", "reason": "missing_credentials"},
                error_message="RESEND_API_KEY or DEFAULT_FROM_EMAIL missing.",
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "from": self.sender_email,
            "to": [recipient],
            "subject": subject,
            "html": body
        }

        try:
            response = requests.post("https://api.resend.com/emails", json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Email sent successfully to {recipient}. Resend ID: {data.get('id')}")
            return SendResult(
                success=True,
                response={
                    "provider": "resend",
                    "status_code": response.status_code,
                    "body": data,
                },
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send email to {recipient}. Error: {str(e)}")
            response_data = {
                "provider": "resend",
                "error": str(e),
            }
            if e.response is not None:
                logger.error(f"Resend Response: {e.response.text}")
                response_data["status_code"] = e.response.status_code
                try:
                    response_data["body"] = e.response.json()
                except ValueError:
                    response_data["body"] = e.response.text
            return SendResult(
                success=False,
                response=response_data,
                error_message=str(e),
            )
