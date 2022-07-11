from django import template

from pastemate.pastes.models import Paste

register = template.Library()


@register.inclusion_tag("pastes/sidebar/public_pastes.html")
def show_public_pastes(count=8):
    public_pastes = Paste.public.all()[:count]
    return {"public_pastes": public_pastes}


@register.inclusion_tag("pastes/sidebar/my_pastes.html")
def show_my_pastes(user, count=8):
    my_pastes = Paste.objects.filter(author=user)[:count]
    return {"my_pastes": my_pastes}


@register.filter()
def tokilobytes(value):
    return "%.2f" % float(value / 1024) + " KB"


@register.filter()
def fulllangname(value):
    return Paste.get_full_language_name(value)
