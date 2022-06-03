from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Paste(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    syntax = models.CharField(max_length=50, blank=True)
    expiration_time = models.TimeField(null=True, blank=True)
    # folder =
    password = models.CharField(max_length=100, blank=True)
    burn_after_read = models.BooleanField(default=False)
    title = models.CharField(max_length=50, blank=True)
