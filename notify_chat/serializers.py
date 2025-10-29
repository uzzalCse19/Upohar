from rest_framework import serializers
from .models import Notification, ChatThread, ChatMessage

class NotificationSerializer(serializers.ModelSerializer):
    recipient = serializers.StringRelatedField()
    class Meta:
        model = Notification
        fields = ['id', 'recipient', 'title', 'message', 'is_read', 'created_at', 'type']

class ChatMessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField()
    class Meta:
        model = ChatMessage
        fields = ['id', 'thread', 'sender', 'message', 'created_at', 'is_read']

class ChatThreadSerializer(serializers.ModelSerializer):
    donor = serializers.StringRelatedField()
    receiver = serializers.StringRelatedField()
    messages = ChatMessageSerializer(many=True, read_only=True)
    class Meta:
        model = ChatThread
        fields = ['id', 'gift', 'donor', 'receiver', 'created_at', 'updated_at', 'messages']
