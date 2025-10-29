from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet, ChatThreadViewSet, ChatMessageViewSet

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet)
router.register(r'chat/threads', ChatThreadViewSet)
router.register(r'chat/messages', ChatMessageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
