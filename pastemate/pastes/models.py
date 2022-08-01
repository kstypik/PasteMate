import tempfile
import uuid
import zipfile
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.files import File
from django.core.files.storage import default_storage
from django.db import models
from django.db.models import Count
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from model_utils.models import TimeStampedModel
from pygments import highlight
from pygments.formatters import HtmlFormatter, ImageFormatter
from pygments.lexers import get_lexer_by_name

from pastemate.pastes import choices

User = get_user_model()

MAX_LINE_LENGTH_FOR_EMBEDS = 111


class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class PublicManager(ActiveManager):
    def get_queryset(self):
        return super().get_queryset().filter(exposure=Paste.Exposure.PUBLIC)

    def languages(self):
        return (
            self.exclude(syntax="text")
            .order_by("syntax")
            .distinct()
            .values("syntax")
            .annotate(used=Count("syntax"))
        )


class Paste(TimeStampedModel):
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

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    content_html = models.TextField(blank=True)
    syntax = models.CharField(
        max_length=50, choices=choices.SYNTAX_HIGHLITHING_CHOICES, default="text"
    )
    expiration_symbol = models.CharField(
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
    password = models.CharField(max_length=128, blank=True)
    burn_after_read = models.BooleanField(default=False)
    title = models.CharField(max_length=50, blank=True)

    filesize = models.IntegerField()

    embeddable_image = models.ImageField(upload_to="embed/", blank=True)

    is_active = models.BooleanField(default=True)

    objects = ActiveManager()
    public = PublicManager()

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return self.title or "Untitled"

    def get_absolute_url(self):
        return reverse("pastes:detail", kwargs={"uuid": self.uuid})

    @property
    def is_private(self):
        return self.exposure == Paste.Exposure.PRIVATE

    @property
    def is_normally_accessible(self):
        return not self.password and not self.burn_after_read

    def is_author(self, user):
        return self.author == user

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

    def create_embeddable_image(self, format=".png"):
        filepath = f"embed/{self.uuid}{format}"
        with tempfile.TemporaryFile() as fh:
            django_file = File(fh)
            django_file.write(self.highlight_syntax(format="image"))
            saved_file = default_storage.save(filepath, django_file)

        return saved_file

    def handle_embeddable_image(self):
        if (
            not self.is_private
            and self.is_normally_accessible
            and not self.longest_line_length > MAX_LINE_LENGTH_FOR_EMBEDS
            and not self.lines_num > 100
        ):
            self.embeddable_image = self.create_embeddable_image()
        else:
            if self.embeddable_image:
                self.embeddable_image.delete()
            self.embeddable_image = ""

    @property
    def longest_line_length(self):
        return len(max(self.content.split("\n"), key=len))

    @property
    def lines_num(self):
        return len(self.content.split("\n"))

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

        if self.expiration_symbol not in to_interval_mapping:
            return None
        return timezone.now() + to_interval_mapping[self.expiration_symbol]

    @staticmethod
    def get_full_language_name(value):
        languages = choices.get_all_languages()
        for language in languages:
            if language[0] == value:
                return language[1]

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = "Untitled"
        self.content_html = self.highlight_syntax()

        self.filesize = self.calculate_filesize()

        self.handle_embeddable_image()

        calculated_expiration = self.calculate_expiration_date()
        if calculated_expiration and not self.expiration_symbol == Paste.NO_CHANGE:
            self.expiration_date = calculated_expiration

        if self.password:
            self.password = make_password(self.password)

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
