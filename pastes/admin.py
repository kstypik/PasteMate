from django.contrib import admin, messages
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import ngettext

from .models import Folder, Paste, Report


@admin.register(Paste)
class PasteAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "syntax",
        "author",
        "burn_after_read",
        "created",
        "expiration_date",
        "folder",
        "is_active",
    ]


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = [
        "moderated",
        "reason",
        "reporter_name",
        "linked_paste",
        "created",
    ]
    list_display_links = ["reason"]
    list_filter = ["moderated"]
    ordering = ["moderated", "created"]
    date_hierarchy = "created"
    actions = ["mark_as_moderated", "mark_as_unmoderated", "deactivate_reported_pastes"]

    @admin.display(description="Name")
    def linked_paste(self, obj):
        return format_html(
            f"{obj.paste} <a href='{obj.paste.get_absolute_url()}'>(view)</a>"
        )

    @admin.action(description="Mark as moderated")
    def mark_as_moderated(self, request, queryset):
        updated = queryset.update(
            moderated=True, moderated_by=request.user, moderated_at=timezone.now()
        )
        self.message_user(
            request,
            ngettext(
                "%d report was successfully marked as moderated.",
                "%d reports were successfully marked as moderated.",
                updated,
            )
            % updated,
            messages.SUCCESS,
        )

    @admin.action(description="Mark as unmoderated")
    def mark_as_unmoderated(self, request, queryset):
        updated = queryset.update(moderated=False)
        self.message_user(
            request,
            ngettext(
                "%d report was successfully marked as unmoderated.",
                "%d reports were successfully marked as unmoderated.",
                updated,
            )
            % updated,
            messages.SUCCESS,
        )

    @admin.action(description="Deactivate pastes from selected reports")
    def deactivate_reported_pastes(self, request, queryset):
        deactivated = queryset.update(
            moderated=True, moderated_by=request.user, moderated_at=timezone.now()
        )
        for report in queryset:
            report.paste.is_active = False
            report.paste.save()
        self.message_user(
            request,
            ngettext(
                "%d reported paste was successfully deactivated.",
                "%d reported pastes were successfully deactivated.",
                deactivated,
            )
            % deactivated,
            messages.SUCCESS,
        )


admin.site.register(Folder)
