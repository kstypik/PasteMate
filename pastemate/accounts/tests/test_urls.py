from django.test import SimpleTestCase
from django.urls import resolve, reverse


class AccountsUrlsTest(SimpleTestCase):
    def test_profile_update(self):
        self.assertEqual(reverse("accounts:profile_update"), "/accounts/edit-profile/")
        self.assertEqual(
            resolve("/accounts/edit-profile/").view_name, "accounts:profile_update"
        )

    def test_delete(self):
        self.assertEqual(reverse("accounts:delete"), "/accounts/delete/")
        self.assertEqual(resolve("/accounts/delete/").view_name, "accounts:delete")

    def test_preferences(self):
        self.assertEqual(reverse("accounts:preferences"), "/accounts/preferences/")
        self.assertEqual(
            resolve("/accounts/preferences/").view_name, "accounts:preferences"
        )

    def test_avatar(self):
        self.assertEqual(reverse("accounts:avatar"), "/accounts/avatar/")
        self.assertEqual(resolve("/accounts/avatar/").view_name, "accounts:avatar")
