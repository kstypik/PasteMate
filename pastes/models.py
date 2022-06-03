import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

User = get_user_model()


class Paste(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    syntax = models.CharField(max_length=50, blank=True)
    expiration_time = models.TimeField(null=True, blank=True)
    # folder =
    password = models.CharField(max_length=100, blank=True)
    burn_after_read = models.BooleanField(default=False)
    title = models.CharField(max_length=50, blank=True)

    def get_absolute_url(self):
        return reverse("pastes:detail", kwargs={"uuid": self.uuid})
