from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import resolve_url
from django.utils.http import urlencode
from hitcount.utils import get_hitcount_model
from hitcount.views import HitCountMixin


def paginate(queryset, page_num, limit):
    paginator = Paginator(queryset, limit)
    try:
        page_obj = paginator.page(page_num)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return page_obj


def count_hit(request, obj):
    hitcount = {}
    hit_count = get_hitcount_model().objects.get_for_object(obj)
    hits = hit_count.hits
    hitcount = {"pk": hit_count.pk}
    hit_count_response = HitCountMixin.hit_count(request, hit_count)
    if hit_count_response.hit_counted:
        hits = hits + 1
    hitcount["hit_counted"] = hit_count_response.hit_counted
    hitcount["hit_message"] = hit_count_response.hit_message
    hitcount["total_hits"] = hits
    return hitcount


def login_redirect_url(url):
    login_url = resolve_url(settings.LOGIN_URL)
    next_url = urlencode({"next": resolve_url(url)})
    return f"{login_url}?{next_url}"
