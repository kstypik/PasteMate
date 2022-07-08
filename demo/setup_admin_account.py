from config.settings.base import env
from pastemate.accounts.models import User

if __name__ == "__main__":
    User.objects.create_superuser(
        username="Admin",
        email="admin@example.com",
        password=env("DJANGO_DEMO_ADMIN_PASS"),
    )
