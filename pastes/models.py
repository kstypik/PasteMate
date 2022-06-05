import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from model_utils.models import TimeStampedModel
from pygments import highlight, lexers
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

    SYNTAX_HIGHLITHING_CHOICES = [
        (lexer[1][0], lexer[0]) for lexer in lexers.get_all_lexers() if lexer[1]
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    content_html = models.TextField(blank=True)
    syntax = models.CharField(
        max_length=50, choices=SYNTAX_HIGHLITHING_CHOICES, default="text"
    )
    expiration_time = models.TimeField(null=True, blank=True)
    exposure = models.CharField(
        max_length=2, choices=Exposure.choices, default=Exposure.PUBLIC
    )
    folder = models.ForeignKey(
        "Folder", on_delete=models.CASCADE, related_name="pastes", null=True, blank=True
    )
    password = models.CharField(max_length=100, blank=True)
    burn_after_read = models.BooleanField(default=False)
    title = models.CharField(max_length=50, blank=True)

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return self.title or "Untitled"

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


class Folder(TimeStampedModel):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="folders"
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)
