import pytest
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

pytestmark = pytest.mark.django_db

SEARCH_URL = reverse("pastes:search")


def test_template_name_correct(auto_login_user):
    client, user = auto_login_user()
    response = client.get(SEARCH_URL)

    assertTemplateUsed(response, "pastes/search_results.html")


def test_finds_appropriate_results(auto_login_user, create_paste):
    client, user = auto_login_user()
    # pastes that should be found
    create_paste(author=user, content="Search me dhfasjhdsafj search")
    create_paste(author=user, content="hfdjs dhfsaj search sdahfjjksd sdha")
    create_paste(author=user, title="Search me", content="dsfajfdhsafdjsah")
    # pastes that shouldn't be found
    create_paste(
        author=user,
        content="fasdfdsafdsafdsa",
    )
    create_paste(
        author=user,
        content="fdsadfsfsdafads",
    )

    response = client.get(SEARCH_URL, {"q": "search"})

    assert len(response.context["page_obj"]) == 3


def test_query_in_context(auto_login_user):
    client, user = auto_login_user()

    response = client.get(SEARCH_URL, {"q": "search"})

    assert response.context["query"] == "search"
