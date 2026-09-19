import logging
from notifications.models import Trigger
from channels import get_channel
from channels.base import SendResult

logger = logging.getLogger(__name__)


def _normalize_send_result(result):
    if isinstance(result, SendResult):
        return result
    return SendResult(success=bool(result), response={"legacy_result": result})


def _build_base_context(user, extra_context):
    """
    Build the default context that every template can reference.
    Merges user fields with any extra context provided by the caller.
    Caller-supplied values override defaults so they can be customised.
    """
    base = {
        "name": user.get_full_name() or user.username,
        "username": user.username,
        "email": user.email or "",
        "phone": user.phone if hasattr(user, "phone") else "",
    }
    base.update(extra_context)  # extra_context wins on conflicts
    return base


def fire_trigger(trigger_key, user, context=None):
    """
    Fire a notification trigger:
      1. Locate the active Trigger by event_key.
      2. Collect its enabled NotificationTemplates.
      3. Enrich context with standard user variables.
      4. Dispatch each template through its channel handler.
      5. Log and isolate individual channel failures.
    """
    if context is None:
        context = {}

    try:
        trigger = Trigger.objects.get(event_key=trigger_key, active=True)
    except Trigger.DoesNotExist:
        logger.warning(f"Trigger '{trigger_key}' not found or inactive. Skipping.")
        return

    templates = trigger.templates.filter(enabled=True)
    if not templates.exists():
        logger.info(f"No enabled templates for trigger '{trigger_key}'.")
        return

    # Enrich with standard user variables so templates get {{name}}, {{email}}, etc.
    enriched_context = _build_base_context(user, context)

    for template in templates:
        channel_handler = get_channel(template.channel)
        if not channel_handler:
            logger.error(f"No handler configured for channel '{template.channel}'.")
            continue

        try:
            logger.info(
                f"Dispatching '{trigger_key}' → {template.channel} for user '{user.username}'"
            )
            send_result = _normalize_send_result(
                channel_handler.send(user, template, enriched_context)
            )
            
            from notifications.models import NotificationLog
            NotificationLog.objects.create(
                trigger=trigger,
                user=user,
                channel=template.channel,
                status='SUCCESS' if send_result.success else 'FAILED',
                response=send_result.response,
                error_message=send_result.error_message,
            )
        except Exception as e:
            # Isolate: one channel failing must not prevent others from firing
            logger.error(
                f"Channel '{template.channel}' failed for trigger '{trigger_key}' "
                f"(user: {user.username})",
                exc_info=True,
            )
            from notifications.models import NotificationLog
            NotificationLog.objects.create(
                trigger=trigger,
                user=user,
                channel=template.channel,
                status='FAILED',
                response={"exception": str(e)},
                error_message=str(e)
            )
