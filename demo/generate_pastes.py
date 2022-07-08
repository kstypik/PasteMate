"""
Generate pastes for pagination testing and noise
"""

from pastemate.accounts.models import User
from pastemate.pastes.models import Paste

if __name__ == "__main__":
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

    for counter in range(221):
        Paste.objects.create(
            author=test_account, title=f"Test paste number {counter}", content=lorem
        )
