import pytest
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

pytestmark = pytest.mark.django_db

LANGUAGES_URL = reverse("pastes:syntax_languages")


def test_template_name_correct(client):
    response = client.get(LANGUAGES_URL)

    assertTemplateUsed(response, "pastes/syntax_languages.html")


def test_displays_language_list_with_count(client, create_paste):
    for _ in range(3):
        create_paste(content="hi", syntax="python")
    for _ in range(2):
        create_paste(content="hi", syntax="javascript")

    response = client.get(LANGUAGES_URL)

    assert response.context["languages"][0]["syntax"] == "javascript"
    assert response.context["languages"][0]["used"] == 2
    assert response.context["languages"][1]["syntax"] == "python"
    assert response.context["languages"][1]["used"] == 3
