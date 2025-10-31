from django.contrib import admin
from .models import Notification, ChatThread, ChatMessage

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'recipient', 'title', 'type', 'is_read', 'created_at']
    list_filter = ['type', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'recipient__email']
    readonly_fields = ['id', 'created_at']
    ordering = ['-created_at']

class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ['id', 'created_at']
    fields = ['id', 'sender', 'message', 'created_at', 'is_read']

@admin.register(ChatThread)
class ChatThreadAdmin(admin.ModelAdmin):
    list_display = ['id', 'gift', 'user1', 'user2', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at', 'user1', 'user2']
    search_fields = ['gift__title', 'user1__email', 'user2__email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [ChatMessageInline]
    ordering = ['-created_at']

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'thread', 'sender', 'message', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at', 'sender']
    search_fields = ['message', 'sender__email', 'thread__gift__title']
    readonly_fields = ['id', 'created_at']
    ordering = ['created_at']
