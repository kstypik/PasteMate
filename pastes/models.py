import tempfile
import uuid
import zipfile
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from model_utils.models import TimeStampedModel
from pygments import highlight, lexers
from pygments.formatters import HtmlFormatter, ImageFormatter
from pygments.lexers import get_lexer_by_name

User = get_user_model()


class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class PublishedManager(ActiveManager):
    def get_queryset(self):
        return super().get_queryset().filter(exposure=Paste.Exposure.PUBLIC)


class Paste(TimeStampedModel):
    class Exposure(models.TextChoices):
        PUBLIC = "PU", "Public"
        UNLISTED = "UN", "Unlisted"
        PRIVATE = "PR", "Private"

    NEVER = ""
    NO_CHANGE = "PRE"
    TEN_MINUTES = "10M"
    ONE_HOUR = "1H"
    ONE_DAY = "1D"
    ONE_WEEK = "1W"
    TWO_WEEKS = "2W"
    ONE_MONTH = "1m"
    SIX_MONTHS = "6M"
    ONE_YEAR = "1Y"

    EXPIRATION_CHOICES = (
        (NO_CHANGE, "Don't Change"),
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

    SYNTAX_HIGHLITHING_CHOICES = (
        ("text", "Text only"),
        (
            "Popular languages",
            (
                ("bash", "Bash"),
                ("c", "C"),
                ("csharp", "C#"),
                ("cpp", "C++"),
                ("css", "CSS"),
                ("html", "HTML"),
                ("json", "JSON"),
                ("java", "Java"),
                ("javascript", "JavaScript"),
                ("lua", "Lua"),
                ("markdown", "Markdown"),
                ("objective-c", "Objective C"),
                ("php", "PHP"),
                ("python", "Python"),
                ("ruby", "Ruby"),
            ),
        ),
        (
            "All languages",
            [
                (lexer[1][0], lexer[0])
                for lexer in lexers.get_all_lexers()
                if lexer[1] and lexer[0] != "Text only"
            ],
        ),
    )

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    content_html = models.TextField(blank=True)
    syntax = models.CharField(
        max_length=50, choices=SYNTAX_HIGHLITHING_CHOICES, default="text"
    )
    expiration_interval_symbol = models.CharField(
        verbose_name="Paste Expiration",
        max_length=3,
        blank=True,
        choices=EXPIRATION_CHOICES,
    )
    expiration_date = models.DateTimeField(null=True, blank=True)
    exposure = models.CharField(
        max_length=2, choices=Exposure.choices, default=Exposure.PUBLIC
    )
    folder = models.ForeignKey(
        "Folder", on_delete=models.CASCADE, related_name="pastes", null=True, blank=True
    )
    password = models.CharField(max_length=100, blank=True)
    burn_after_read = models.BooleanField(default=False)
    title = models.CharField(max_length=50, blank=True)

    filesize = models.IntegerField()

    embeddable_image = models.ImageField(upload_to="embed/", blank=True)

    is_active = models.BooleanField(default=True)

    objects = ActiveManager()
    published = PublishedManager()

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return self.title or "Untitled"

    def get_absolute_url(self):
        return reverse("pastes:detail", kwargs={"uuid": self.uuid})

    def calculate_filesize(self):
        return len(self.content.encode("utf-8"))

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

    @classmethod
    def make_backup_archive(cls, destination, user_obj):
        archive = zipfile.ZipFile(destination, "w")

        pastes = cls.objects.filter(author=user_obj)
        for paste in pastes:
            filename = (
                f"{paste.title}-{paste.uuid}.txt"
                if paste.title != "Untitled"
                else f"{paste.uuid}.txt"
            )
            archive.writestr(filename, paste.content)

        return archive

    def calculate_expiration_date(self):
        if not self.expiration_interval_symbol:
            return None

        to_interval_mapping = {
            Paste.TEN_MINUTES: timedelta(minutes=10),
            Paste.ONE_HOUR: timedelta(hours=1),
            Paste.ONE_DAY: timedelta(days=1),
            Paste.ONE_WEEK: timedelta(weeks=1),
            Paste.TWO_WEEKS: timedelta(weeks=2),
            Paste.ONE_MONTH: timedelta(days=30),
            Paste.SIX_MONTHS: timedelta(days=180),
            Paste.ONE_YEAR: timedelta(days=365),
        }
        return timezone.now() + to_interval_mapping[self.expiration_interval_symbol]

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = "Untitled"
        self.content_html = self.highlight_syntax()
        if (
            not self.exposure == Paste.Exposure.PRIVATE
            or not self.password
            or not self.burn_after_read
        ):
            self.embeddable_image = self.make_embeddable_image()
        self.filesize = self.calculate_filesize()

        self.expiration_date = self.calculate_expiration_date()

        super().save(*args, **kwargs)


class Folder(TimeStampedModel):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="folders"
    )

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "created_by"], name="unique_folder"
            ),
            models.UniqueConstraint(
                fields=["slug", "created_by"], name="unique_folder_slug"
            ),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            "pastes:user_folder",
            kwargs={"username": self.created_by.username, "folder_slug": self.slug},
        )

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


class Report(TimeStampedModel):
    paste = models.ForeignKey(Paste, on_delete=models.CASCADE)
    reason = models.TextField()
    reporter_name = models.CharField(max_length=100)
    moderated = models.BooleanField(default=False)
    moderated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    moderated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Report by {self.reporter_name}"
