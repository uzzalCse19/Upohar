
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UpoharPost 
from notify_chat.models import Notification
from users.models import User

@receiver(post_save, sender=UpoharPost)
def create_upohar_notification(sender, instance, created, **kwargs):
    if created:
        recipients = User.objects.exclude(id=instance.donor.id)  # For ALL except donor
        donor_name = instance.donor.name if instance.donor.name else instance.donor.email
        for user in recipients:
            Notification.objects.create(
                recipient=user,
               title=f"New Upohar Posted by {donor_name}",
                message=f"{donor_name} posted a new gift: {instance.title}",
                type='upohar_request'
            )
