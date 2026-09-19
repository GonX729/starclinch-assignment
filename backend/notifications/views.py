from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .models import Trigger, NotificationTemplate, PushSubscription, NotificationLog
from .serializers import TriggerSerializer, NotificationTemplateSerializer, NotificationLogSerializer
from .push_serializers import PushSubscriptionSerializer
from channels.base import SendResult


def _normalize_send_result(result):
    if isinstance(result, SendResult):
        return result
    return SendResult(success=bool(result), response={"legacy_result": result})


class TriggerViewSet(viewsets.ModelViewSet):
    """
    API for managing Triggers.
    Supports GET, POST, PUT, DELETE.
    """
    permission_classes = [IsAdminUser]
    queryset = Trigger.objects.all().order_by('-created_at')
    serializer_class = TriggerSerializer


class NotificationTemplateViewSet(viewsets.ModelViewSet):
    """
    API for managing NotificationTemplates.
    Supports GET, POST, PUT, DELETE.
    """
    permission_classes = [IsAdminUser]
    queryset = NotificationTemplate.objects.all().select_related('trigger').order_by('-created_at')
    serializer_class = NotificationTemplateSerializer

    @action(detail=True, methods=['patch'])
    def toggle(self, request, pk=None):
        """
        Toggle enabled/disabled for a template.
        PATCH /api/admin/templates/:id/toggle/
        """
        template = self.get_object()
        template.enabled = not template.enabled
        template.save(update_fields=['enabled'])
        return Response({
            'status': 'success',
            'enabled': template.enabled,
            'message': f'Template {"enabled" if template.enabled else "disabled"} successfully.'
        }, status=status.HTTP_200_OK)

    def _send_single_template(self, template, user):
        from channels import get_channel
        from triggers.registry import _build_base_context

        channel_handler = get_channel(template.channel)
        if not channel_handler:
            NotificationLog.objects.create(
                trigger=template.trigger,
                user=user,
                channel=template.channel,
                status='FAILED',
                response={"reason": "missing_channel_handler"},
                error_message=f"No handler configured for channel '{template.channel}'.",
            )
            return False

        context = _build_base_context(user, {
            'test': True,
            'triggered_by': user.username,
        })
        send_result = _normalize_send_result(channel_handler.send(user, template, context))
        NotificationLog.objects.create(
            trigger=template.trigger,
            user=user,
            channel=template.channel,
            status='SUCCESS' if send_result.success else 'FAILED',
            response=send_result.response,
            error_message=send_result.error_message,
        )
        return send_result.success

    @action(detail=True, methods=['post'], url_path='test-send')
    def test_send(self, request, pk=None):
        """
        Send only this template/channel to the logged-in admin.
        POST /api/admin/templates/:id/test-send/
        """
        template = self.get_object()
        success = self._send_single_template(template, request.user)

        if not success:
            return Response({
                'status': 'error',
                'message': (
                    f'Test send failed for {template.trigger.event_key} / '
                    f'{template.channel}. Check admin contact details, subscription, '
                    'environment keys, and server logs.'
                ),
            }, status=status.HTTP_502_BAD_GATEWAY)

        return Response({
            'status': 'success',
            'message': (
                f'Test notification sent for {template.trigger.event_key} / '
                f'{template.channel}.'
            ),
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """
        Backward-compatible alias for older frontend calls.
        POST /api/templates/:id/test/
        """
        return self.test_send(request, pk=pk)


class NotificationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API for viewing Notification Logs.
    Admin only.
    """
    permission_classes = [IsAdminUser]
    queryset = NotificationLog.objects.all().select_related('trigger', 'user').order_by('-created_at')
    serializer_class = NotificationLogSerializer


class PushSubscribeView(APIView):
    """
    POST /api/push/subscribe/
    Register a browser OneSignal player_id for the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PushSubscriptionSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            sub = serializer.save()
            return Response({
                'status': 'success',
                'message': 'Browser push subscription registered.',
                'id': str(sub.id),
                'player_id': sub.player_id,
            }, status=status.HTTP_201_CREATED)
        return Response({'status': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """
        DELETE /api/push/subscribe/
        Unregister the player_id sent in the request body.
        """
        player_id = request.data.get('player_id')
        if not player_id:
            return Response({'status': 'error', 'message': 'player_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        deleted, _ = PushSubscription.objects.filter(
            user=request.user, player_id=player_id
        ).delete()

        if deleted:
            return Response({'status': 'success', 'message': 'Subscription removed.'})
        return Response({'status': 'error', 'message': 'Subscription not found.'}, status=status.HTTP_404_NOT_FOUND)
