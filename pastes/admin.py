from django.contrib import admin

from .models import Paste


@admin.register(Paste)
class PasteAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "syntax",
        "author",
        "burn_after_read",
        "created",
        "expiration_time",
    ]
