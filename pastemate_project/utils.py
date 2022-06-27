from django.conf import settings
from django.shortcuts import resolve_url
from django.utils.http import urlencode


def login_redirect_url(url):
    login_url = resolve_url(settings.LOGIN_URL)
    next_url = urlencode({"next": resolve_url(url)})
    return f"{login_url}?{next_url}"
