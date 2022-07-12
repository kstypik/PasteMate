from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import resolve_url
from django.utils.http import urlencode


def paginate(queryset, page_num, limit):
    paginator = Paginator(queryset, limit)
    try:
        page_obj = paginator.page(page_num)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return page_obj


def login_redirect_url(url):
    login_url = resolve_url(settings.LOGIN_URL)
    next_url = urlencode({"next": resolve_url(url)})
    return f"{login_url}?{next_url}"
