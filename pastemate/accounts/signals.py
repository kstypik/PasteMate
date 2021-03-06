from django.db.models.signals import post_save
from django.dispatch import receiver
from pinax.messages.models import Message

from pastemate.accounts.models import Preferences, User


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Preferences.objects.create(user=instance)


@receiver(post_save, sender=User)
def send_welcome_message(sender, instance, created, **kwargs):
    if created:
        try:
            admin_account = User.objects.get(id=1)
        except User.DoesNotExist:
            return

        subject = "Welcome to PasteMate!"
        content = f"""Hello {instance.username},
    Good to see that you have decided to join our community!
    If you have any questions regarding the website, please feel free to contact us.

    Kind regards,
    PasteMate team"""
        Message.new_message(
            from_user=admin_account,
            to_users=[instance],
            subject=subject,
            content=content,
        )
