from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UpoharRequest, UpoharPost

# Notify donor on new request
@receiver(post_save, sender=UpoharRequest)
def notify_donor_on_request(sender, instance, created, **kwargs):
    if created:
        # Add notification logic here (email, in-app, etc.)
        pass

# Auto-mark gift as completed when request status is approved
@receiver(post_save, sender=UpoharRequest)
def auto_complete_gift(sender, instance, **kwargs):
    if instance.status == 'approved':
        gift = instance.gift
        gift.status = 'completed'
        gift.save()

