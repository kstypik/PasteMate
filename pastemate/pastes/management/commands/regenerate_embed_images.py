from django.core.management.base import BaseCommand

from pastemate.pastes.models import Paste


class Command(BaseCommand):
    help = "Generates demo pastes"

    def handle(self, *args, **options):

        self.stdout.write("Regenerating embeddable images...", ending=" ")
        self.stdout.flush()

        no_embed_pastes = Paste.objects.filter(embeddable_image="")
        for paste in no_embed_pastes:
            if not (paste.is_private or not paste.is_normally_accessible):
                paste.embeddable_image = paste.make_embeddable_image()
                paste.save()

        self.stdout.write(self.style.SUCCESS("OK"))
