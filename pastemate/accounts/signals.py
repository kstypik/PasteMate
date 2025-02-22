from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import Preferences, User


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Preferences.objects.create(user=instance)
