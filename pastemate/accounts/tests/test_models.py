from django.test import TestCase

from pastemate.accounts.models import User


class UserModelTest(TestCase):
    def test___str__(self):
        user = User.objects.create_user(username="John")
        self.assertEqual(user.__str__(), user.username)
        self.assertEqual(str(user), user.username)

    def test_get_absolute_url(self):
        user = User.objects.create_user(username="John")
        url = user.get_absolute_url()

        self.assertEqual(url, f"/user/{user.username}/")


class PreferencesModelTest(TestCase):
    def test___str__(self):
        user = User.objects.create_user(username="John")

        self.assertEqual(user.preferences.__str__(), f"Preferences of {user.username}")
        self.assertEqual(str(user.preferences), f"Preferences of {user.username}")
