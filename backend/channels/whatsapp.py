import logging
from .base import BaseChannel, SendResult
from .whatsapp_service import WhatsAppService
from .renderer import render_template

logger = logging.getLogger(__name__)
whatsapp_service = WhatsAppService()

class WhatsAppChannel(BaseChannel):
    def send(self, user, template, context):
        if not user.phone:
            logger.error(f"User {user.username} has no phone number configured. Cannot send WhatsApp.")
            return SendResult(
                success=False,
                response={"reason": "missing_user_phone"},
                error_message="User has no phone number configured.",
            )
            
        body = render_template(template.body, context)
            
        logger.info(f"[WHATSAPP] Dispatching message to {user.phone}")
        return whatsapp_service.send_message(
            recipient_phone=user.phone,
            message=body
        )
