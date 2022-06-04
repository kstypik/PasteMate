import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from model_utils.models import TimeStampedModel
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name

User = get_user_model()


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(exposure=Paste.Exposure.PUBLIC)


class Paste(TimeStampedModel):
    class Exposure(models.TextChoices):
        PUBLIC = "PU", "Public"
        UNLISTED = "UN", "Unlisted"
        PRIVATE = "PR", "Private"

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    content_html = models.TextField(blank=True)
    syntax = models.CharField(max_length=50, blank=True)
    expiration_time = models.TimeField(null=True, blank=True)
    exposure = models.CharField(
        max_length=2, choices=Exposure.choices, default=Exposure.PUBLIC
    )
    # folder =
    password = models.CharField(max_length=100, blank=True)
    burn_after_read = models.BooleanField(default=False)
    title = models.CharField(max_length=50, blank=True)

    objects = models.Manager()
    published = PublishedManager()

    def get_absolute_url(self):
        return reverse("pastes:detail", kwargs={"uuid": self.uuid})

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = "Untitled"
        if self.syntax:
            lexer = get_lexer_by_name(self.syntax, stripall=True)
            self.content_html = highlight(
                self.content, lexer, HtmlFormatter(linenos=True)
            )
        super().save(*args, **kwargs)
