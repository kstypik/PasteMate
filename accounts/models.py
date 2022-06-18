from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from pastes import choices


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


class Preferences(models.Model):
    class Exposure(models.TextChoices):
        PUBLIC = choices.PUBLIC
        UNLISTED = choices.UNLISTED
        PRIVATE = choices.PRIVATE

    NEVER = choices.NEVER
    NO_CHANGE = choices.NO_CHANGE
    TEN_MINUTES = choices.TEN_MINUTES
    ONE_HOUR = choices.ONE_HOUR
    ONE_DAY = choices.ONE_DAY
    ONE_WEEK = choices.ONE_WEEK
    TWO_WEEKS = choices.TWO_WEEKS
    ONE_MONTH = choices.ONE_MONTH
    SIX_MONTHS = choices.SIX_MONTHS
    ONE_YEAR = choices.ONE_YEAR

    EXPIRATION_CHOICES = (
        (NEVER, "Never"),
        (TEN_MINUTES, "10 minutes"),
        (ONE_HOUR, "1 Hour"),
        (ONE_DAY, "1 Day"),
        (ONE_WEEK, "1 Week"),
        (TWO_WEEKS, "2 Weeks"),
        (ONE_MONTH, "1 Month"),
        (SIX_MONTHS, "6 Month"),
        (ONE_YEAR, "1 Year"),
    )

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="preferences"
    )
    default_syntax = models.CharField(
        verbose_name="Default Syntax",
        max_length=50,
        choices=choices.SYNTAX_HIGHLITHING_CHOICES,
        default="text",
    )
    default_expiration_interval_symbol = models.CharField(
        verbose_name="Default Expiration",
        max_length=3,
        blank=True,
        choices=EXPIRATION_CHOICES,
        default=NEVER,
    )
    default_exposure = models.CharField(
        verbose_name="Default Exposure",
        max_length=2,
        choices=Exposure.choices,
        default=Exposure.PUBLIC,
    )

    def __str__(self):
        return f"Preferences of {self.user}"
