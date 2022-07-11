from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator


def paginate(queryset, page_num, limit):
    paginator = Paginator(queryset, limit)
    try:
        page_obj = paginator.page(page_num)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return page_obj
