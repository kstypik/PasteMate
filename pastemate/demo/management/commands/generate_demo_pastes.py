from django.core.management.base import BaseCommand

from pastemate.accounts.models import User
from pastemate.pastes.models import Paste


class Command(BaseCommand):
    help = "Generates demo pastes"

    def handle(self, *args, **options):
        test_account = User.objects.get(id=2)

        lorem = """Lorem ipsum dolor sit amet, consectetur adipiscing elit.
In eget dapibus eros, at faucibus magna.
Morbi eget mollis lectus, eu ornare dolor.
Maecenas et imperdiet nibh.
Mauris tincidunt augue eget augue fermentum, eget consectetur lorem feugiat.
Nunc sed sagittis turpis.
Cras dictum sodales venenatis.
Aenean id tellus vitae felis lobortis dignissim.
Nam hendrerit massa nec tellus convallis faucibus.
Phasellus ut volutpat purus."""

        self.stdout.write("Generating demo pastes...")
        self.stdout.flush()

        for counter in range(221):
            Paste.objects.create(
                author=test_account, title=f"Test paste number {counter}", content=lorem
            )

        self.stdout.write(self.style.SUCCESS("OK"))
