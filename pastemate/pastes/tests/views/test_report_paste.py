import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertTemplateUsed

from pastes import forms
from pastes.models import Paste, Report

pytestmark = pytest.mark.django_db


def template_name_correct(client, create_paste):
    paste = create_paste()
    report_url = reverse("pastes:report", args=[paste.uuid])

    response = client.get(report_url)

    assertTemplateUsed(response, "pastes/report.html")


def test_form_class_correct(client, create_paste):
    paste = create_paste()
    report_url = reverse("pastes:report", args=[paste.uuid])

    response = client.get(report_url)

    assert isinstance(response.context["form"], forms.ReportForm)


def test_reported_paste_in_context(client, create_paste):
    paste = create_paste()
    report_url = reverse("pastes:report", args=[paste.uuid])

    response = client.get(report_url)

    assert response.context["reported_paste"] == paste


def test_can_report_paste(client, create_paste):
    paste = create_paste()
    report_url = reverse("pastes:report", args=[paste.uuid])
    data = {"reason": "Testing", "reporter_name": "Tester"}

    client.post(report_url, data=data)

    created_report = Report.objects.first()
    assert Report.objects.count() == 1
    assert created_report.paste == paste


def test_redirects_to_paste_on_success(client, create_paste):
    paste = create_paste()
    report_url = reverse("pastes:report", args=[paste.uuid])
    data = {"reason": "Testing", "reporter_name": "Tester"}

    response = client.post(report_url, data=data)

    assertRedirects(response, paste.get_absolute_url())


def test_cannot_report_burnable_paste(client, create_paste):
    burnable_paste = create_paste(burn_after_read=True)
    report_url = reverse("pastes:report", args=[burnable_paste.uuid])

    response = client.get(report_url)

    assert response.status_code == 404


def test_cannot_report_password_protected_paste(client, create_paste):
    paste_with_pass = create_paste(password="pass123")
    report_url = reverse("pastes:report", args=[paste_with_pass.uuid])

    response = client.get(report_url)

    assert response.status_code == 404


def test_cannot_report_private_paste(client, create_paste):
    private_paste = create_paste(exposure=Paste.Exposure.PRIVATE)
    report_url = reverse("pastes:report", args=[private_paste.uuid])

    response = client.get(report_url)

    assert response.status_code == 404


def test_cannot_report_users_own_pastes(auto_login_user, create_paste):
    client, user = auto_login_user()
    paste = create_paste(author=user)
    report_url = reverse("pastes:report", args=[paste.uuid])

    response = client.get(report_url)

    assert response.status_code == 404
