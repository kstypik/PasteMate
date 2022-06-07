import tempfile
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from model_utils.models import TimeStampedModel
from pygments import highlight, lexers
from pygments.formatters import HtmlFormatter, ImageFormatter
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

    embeddable_image = models.ImageField(upload_to="embed/", blank=True)

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return self.title or "Untitled"

    def get_absolute_url(self):
        return reverse("pastes:detail", kwargs={"uuid": self.uuid})

    def highlight_syntax(self, format="html"):
        lexer = get_lexer_by_name(self.syntax, stripall=True)
        if format == "html":
            formatter = HtmlFormatter(linenos=True)
        elif format == "image":
            formatter = ImageFormatter()
        else:
            return NotImplemented

        return highlight(self.content, lexer, formatter)

    def make_embeddable_image(self, format=".png"):
        filepath = f"embed/{self.uuid}{format}"
        with open(settings.MEDIA_ROOT / filepath, "wb") as fh:
            fh.write(self.highlight_syntax(format="image"))

        return filepath

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = "Untitled"
        self.content_html = self.highlight_syntax()
        self.embeddable_image = self.make_embeddable_image()
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
