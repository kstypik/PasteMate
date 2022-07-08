import os

from pastemate.accounts.models import User

if __name__ == "__main__":
    User.objects.create_superuser(
        username="Admin",
        email="admin@example.com",
        password=os.environ.get("DJANGO_DEMO_ADMIN_PASS"),
    )
