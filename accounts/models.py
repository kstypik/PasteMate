from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    first_name = None
    last_name = None
    email = models.EmailField(_("email address"), unique=True)

    website = models.URLField(blank=True)
    location = models.CharField(max_length=150, blank=True)
    avatar = models.ImageField(
        upload_to="avatars/", blank=True, default="default_avatar.png"
    )

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse("pastes:user_pastes", kwargs={"username": self.username})
