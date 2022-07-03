from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.test import TestCase

from ..forms import AccountDeleteForm

User = get_user_model()


class AccountDeleteFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="Test", email="test@test.com", password="test123"
        )

    def test_form_raises_error_when_password_incorrect(self):
        request = HttpRequest()
        request.user = self.user
        form = AccountDeleteForm(request=request, data={"password": "incorrect_pass"})

        self.assertEqual(form.errors["password"], ["Entered password is invalid."])

    def test_form_is_valid_when_password_correct(self):
        request = HttpRequest()
        request.user = self.user
        form = AccountDeleteForm(request=request, data={"password": "test123"})

        self.assertTrue(form.is_valid())
