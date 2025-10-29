from django.db import models

# Create your models here.
import uuid
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

import uuid
from django.db import models
from django.utils import timezone
from users.models import User

class UpoharPost(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('requested', 'Requested'),
        ('completed', 'Completed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donated_gifts')
    receiver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_gifts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    title = models.CharField(max_length=200)
    description = models.TextField()
    city = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='gifts/', null=True, blank=True)  

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    created_at = models.DateTimeField(default=timezone.now) 
    updated_at = models.DateTimeField(auto_now=True)  

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


from django.db import models

class UpoharImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    gift = models.ForeignKey(
        'UpoharPost',
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='gifts/')
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.gift.title} ({'Primary' if self.is_primary else 'Secondary'})"



from django.db import models
from users.models import User
import uuid
from django.utils import timezone

class UpoharRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    gift = models.ForeignKey(UpoharPost, on_delete=models.CASCADE, related_name='requests')
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gift_requests')

    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.requester.email} → {self.gift.title} ({self.status})"

    class Meta:
        unique_together = ('gift', 'requester')
        ordering = ['-created_at']
