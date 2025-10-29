from django.db import models

# Create your models here.

from django.db import models
from users.models import User
import uuid
from django.utils import timezone

class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    # Optional: Notification type (for filtering)
    NOTIFICATION_TYPES = [
        ('upohar_request', 'Upohar Request'),
        ('request_approved', 'Request Approved'),
        ('request_rejected', 'Request Rejected'),
        ('chat_message', 'Chat Message'),
    ]
    type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, blank=True)

    def __str__(self):
        return f"{self.title} → {self.recipient.email}"

    class Meta:
        ordering = ['-created_at']

from django.db import models
from users.models import User
from upohars.models import UpoharPost
import uuid
from django.utils import timezone

class ChatThread(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    gift = models.ForeignKey(UpoharPost, on_delete=models.CASCADE, related_name='chat_threads')
    donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donor_threads')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver_threads')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('gift', 'donor', 'receiver')
        ordering = ['-created_at']

    def __str__(self):
        return f"Chat: {self.gift.title} ({self.donor.email} ↔ {self.receiver.email})"


class ChatMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    thread = models.ForeignKey(ChatThread, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message from {self.sender.email} in {self.thread.gift.title}"


