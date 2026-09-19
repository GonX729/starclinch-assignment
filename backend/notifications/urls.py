from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TriggerViewSet, NotificationTemplateViewSet, PushSubscribeView, NotificationLogViewSet

router = DefaultRouter()
router.register(r'triggers', TriggerViewSet, basename='trigger')
router.register(r'templates', NotificationTemplateViewSet, basename='template')
router.register(r'logs', NotificationLogViewSet, basename='log')

urlpatterns = [
    path('admin/', include(router.urls)),
    path('', include(router.urls)),
    path('push/subscribe/', PushSubscribeView.as_view(), name='push_subscribe'),
]
