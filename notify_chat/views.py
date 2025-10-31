from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions
from .models import Notification, ChatThread, ChatMessage
from .serializers import NotificationSerializer, ChatThreadSerializer, ChatMessageSerializer


from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Notification
from .serializers import NotificationSerializer

# Pagination (optional)
from rest_framework.pagination import PageNumberPagination

class NotificationPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class NotificationViewSet(viewsets.ModelViewSet):
    """
    Notification ViewSet with improvements:
    - Only shows notifications for logged-in user
    - Filter by type or read/unread
    - Unread count endpoint
    - Pagination
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['type', 'is_read']
    pagination_class = NotificationPagination
    queryset = Notification.objects.all() 
    def get_queryset(self):
        # Only return notifications for the current user
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')
    def perform_create(self, serializer):
        """
        Automatically set recipient as the logged-in user
        when creating notification manually (e.g. from Swagger)
        """
        serializer.save(recipient=self.request.user)
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """
        Returns the count of unread notifications for the logged-in user
        """
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return Response({'unread_count': count})


class ChatThreadViewSet(viewsets.ModelViewSet):
    queryset = ChatThread.objects.all()
    serializer_class = ChatThreadSerializer
    permission_classes = [permissions.IsAuthenticated]

class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
