import logging
from .base import BaseChannel, SendResult
from .email_service import EmailService
from .renderer import render_template

logger = logging.getLogger(__name__)
email_service = EmailService()

class EmailChannel(BaseChannel):
    def send(self, user, template, context):
        if not user.email:
            logger.error(f"User {user.username} has no email address configured. Cannot send email.")
            return SendResult(
                success=False,
                response={"reason": "missing_user_email"},
                error_message="User has no email address configured.",
            )
            
        subject = render_template(template.subject or "Notification from System", context)
        body = render_template(template.body, context)
            
        logger.info(f"[EMAIL] Dispatching email to {user.email}")
        return email_service.send_email(
            recipient=user.email,
            subject=subject,
            body=body
        )
