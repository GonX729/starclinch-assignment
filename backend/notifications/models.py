import uuid
from django.db import models
from django.conf import settings

class ChannelChoices(models.TextChoices):
    WHATSAPP = 'WHATSAPP', 'WhatsApp'
    EMAIL = 'EMAIL', 'Email'
    WEB_PUSH = 'WEB_PUSH', 'Web Push'

class Trigger(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    event_key = models.CharField(max_length=50, unique=True, db_index=True)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.event_key})"


class NotificationTemplate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    trigger = models.ForeignKey(Trigger, on_delete=models.CASCADE, related_name='templates')
    channel = models.CharField(max_length=20, choices=ChannelChoices.choices)
    subject = models.CharField(max_length=255, blank=True, help_text="Used for Email channel")
    body = models.TextField(help_text="Supports variable mapping via {{ variable }} syntax")
    enabled = models.BooleanField(default=True)
    variable_mappings = models.JSONField(default=dict, blank=True, help_text="e.g. {'user_name': 'user.username'}")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('trigger', 'channel')

    def __str__(self):
        return f"{self.trigger.event_key} - {self.channel}"


class PushSubscription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='push_subscriptions')
    # OneSignal assigns a player_id when the browser subscribes via the OneSignal SDK
    player_id = models.CharField(max_length=255, unique=True, db_index=True, default='')
    # Optional: track which browser/device this subscription is from
    user_agent = models.CharField(max_length=512, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"Push Sub ({self.player_id}) for {self.user}"


class NotificationLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    trigger = models.ForeignKey(Trigger, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    channel = models.CharField(max_length=20, choices=ChannelChoices.choices)
    status = models.CharField(max_length=20, choices=[('SUCCESS', 'Success'), ('FAILED', 'Failed')])
    response = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.channel} to {self.user} - {self.status}"
