from django.core.management.base import BaseCommand

from pastes.models import Paste


class Command(BaseCommand):
    help = "Generates demo pastes"

    def handle(self, *args, **options):
        self.stdout.write("Regenerating embeddable images...", ending=" ")
        self.stdout.flush()

        no_embed_pastes = Paste.objects.filter(embeddable_image="")
        for paste in no_embed_pastes:
            paste.handle_embeddable_image()
            paste.save()

        self.stdout.write(self.style.SUCCESS("OK"))
