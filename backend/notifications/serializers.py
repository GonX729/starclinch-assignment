from rest_framework import serializers
from .models import Trigger, NotificationTemplate, ChannelChoices, NotificationLog


class TriggerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trigger
        fields = ['id', 'name', 'event_key', 'description', 'active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationTemplateSerializer(serializers.ModelSerializer):
    trigger_detail = TriggerSerializer(source='trigger', read_only=True)

    class Meta:
        model = NotificationTemplate
        fields = [
            'id', 'trigger', 'trigger_detail', 'channel', 'subject', 'body',
            'enabled', 'variable_mappings', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        channel = attrs.get('channel') or (self.instance.channel if self.instance else None)
        subject = attrs.get('subject', self.instance.subject if self.instance else '')
        if channel == ChannelChoices.EMAIL and not subject:
            raise serializers.ValidationError({'subject': 'Subject is required for EMAIL channel.'})
        return attrs

class NotificationLogSerializer(serializers.ModelSerializer):
    trigger_name = serializers.CharField(source='trigger.event_key', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = NotificationLog
        fields = '__all__'
