from rest_framework import serializers
from .models import PushSubscription


class PushSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushSubscription
        fields = ['id', 'player_id', 'user_agent', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        user = self.context['request'].user
        player_id = validated_data['player_id']

        # Upsert: update user_agent if already registered for this player
        sub, _ = PushSubscription.objects.update_or_create(
            player_id=player_id,
            defaults={
                'user': user,
                'user_agent': validated_data.get('user_agent', '')
            }
        )
        return sub
