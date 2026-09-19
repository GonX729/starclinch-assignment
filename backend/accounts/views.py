from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomLoginView(TokenObtainPairView):
    """
    POST /api/auth/login/
    Returns JWT tokens and fires the LOGIN trigger.
    """
    permission_classes = []  # public

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            username = request.data.get('username', '')
            try:
                user = User.objects.get(username=username)
                response.data['is_staff'] = user.is_staff
                from triggers.registry import fire_trigger
                fire_trigger('LOGIN', user, context={
                    'ip_address': request.META.get('REMOTE_ADDR', '')
                })
            except User.DoesNotExist:
                pass
        return response


class LogoutView(APIView):
    """
    POST /api/auth/logout/
    Blacklists the refresh token and fires the LOGOUT trigger.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass  # token already blacklisted or invalid — proceed anyway

        from triggers.registry import fire_trigger
        fire_trigger('LOGOUT', request.user, context={
            'ip_address': request.META.get('REMOTE_ADDR', '')
        })

        return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)
