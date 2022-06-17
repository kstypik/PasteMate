from django.core.management.base import BaseCommand
from django.db.models import F
from django.db.models.functions import Now
from django.db.models.lookups import GreaterThanOrEqual
from pastes.models import Paste


class Command(BaseCommand):
    help = "Deletes expired pastes"

    def add_arguments(self, parser):
        parser.add_argument(
            "--only-show",
            action="store_true",
            help="Don't delete, only show what will be deleted",
        )

    def handle(self, *args, **options):
        qs = Paste.objects.filter(
            GreaterThanOrEqual(Now(), F("created") + F("expiration_time"))
        )
        removed_pastes_num = qs.count()
        if removed_pastes_num > 0:
            if options["only_show"]:
                self.stdout.write("Pastes to delete: ", qs)
            else:
                qs.delete()
                self.stdout.write(
                    self.style.SUCCESS(
                        "Successfully deleted %s expired pastes" % removed_pastes_num
                    )
                )
        else:
            self.stdout.write("No expired pastes to remove")
