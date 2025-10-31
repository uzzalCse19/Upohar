from django.db import models
from django.db import models
from django.utils import timezone
from users.models import User
# Create your mode
from django.db import models
from cloudinary.models import CloudinaryField
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name




class UpoharPost(models.Model):
    TYPE_CHOICES = [
        ('donation', 'Donation'),
        ('exchange', 'Exchange'),
    ]

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('requested', 'Requested'),
        ('completed', 'Completed'),
    ]
    donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donated_gifts')
    receiver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_gifts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='donation')  # ⬅️ নতুন ফিল্ড

    title = models.CharField(max_length=200)
    description = models.TextField()
    city = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='gifts/', null=True, blank=True)

    # Exchange-specific fields
    exchange_item_name = models.CharField(max_length=200, blank=True, null=True)
    exchange_item_description = models.TextField(blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.get_type_display()} - {self.get_status_display()})"


from django.db import models

class UpoharImage(models.Model):
    gift = models.ForeignKey(
        'UpoharPost',
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = CloudinaryField('image', null=True, blank=True)
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.gift.title} ({'Primary' if self.is_primary else 'Secondary'})"



from django.db import models
from users.models import User

from django.utils import timezone

class UpoharRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

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
