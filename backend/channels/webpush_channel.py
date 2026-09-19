import logging
from .base import BaseChannel, SendResult
from .webpush_service import WebPushService
from .renderer import render_template

logger = logging.getLogger(__name__)
webpush_service = WebPushService()


class WebPushChannel(BaseChannel):
    def send(self, user, template, context):
        # Fetch all OneSignal player IDs registered for this user
        player_ids = list(
            user.push_subscriptions.values_list('player_id', flat=True)
        )

        if not player_ids:
            logger.info(f"[WEB_PUSH] No push subscriptions found for user {user.username}. Skipping.")
            return SendResult(
                success=False,
                response={"reason": "no_push_subscriptions"},
                error_message="No browser push subscriptions found for user.",
            )

        body = render_template(template.body, context)
        title = render_template(template.subject or "Notification", context)

        logger.info(f"[WEB_PUSH] Dispatching to {len(player_ids)} subscription(s) for user {user.username}")
        return webpush_service.send_to_user_players(player_ids, title=title, message=body)
