import os
import logging
import requests
from dotenv import load_dotenv
from .base import SendResult

load_dotenv()
logger = logging.getLogger(__name__)

class WhatsAppService:
    def __init__(self):
        self.access_token = os.getenv('WHATSAPP_ACCESS_TOKEN')
        self.phone_number_id = os.getenv('PHONE_NUMBER_ID')
        
    def send_message(self, recipient_phone, message):
        if not self.access_token or not self.phone_number_id:
            logger.error("Cannot send WhatsApp: WHATSAPP_ACCESS_TOKEN or PHONE_NUMBER_ID missing.")
            return SendResult(
                success=False,
                response={"provider": "whatsapp", "reason": "missing_credentials"},
                error_message="WHATSAPP_ACCESS_TOKEN or PHONE_NUMBER_ID missing.",
            )

        # WhatsApp Cloud API Endpoint (Graph API)
        url = f"https://graph.facebook.com/v20.0/{self.phone_number_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": recipient_phone,
            "type": "text",
            "text": {
                "body": message
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            logger.info(f"WhatsApp sent successfully to {recipient_phone}. MessageID: {data.get('messages', [{}])[0].get('id')}")
            return SendResult(
                success=True,
                response={
                    "provider": "whatsapp",
                    "status_code": response.status_code,
                    "body": data,
                },
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send WhatsApp to {recipient_phone}. Error: {str(e)}")
            response_data = {
                "provider": "whatsapp",
                "error": str(e),
            }
            if e.response is not None:
                logger.error(f"WhatsApp API Response: {e.response.text}")
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
