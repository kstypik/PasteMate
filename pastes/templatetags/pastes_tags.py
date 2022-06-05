from django import template

from ..models import Paste

register = template.Library()


@register.inclusion_tag("pastes/sidebar/public_pastes.html")
def show_public_pastes(count=8):
    public_pastes = Paste.published.all()[:count]
    return {"public_pastes": public_pastes}


@register.inclusion_tag("pastes/sidebar/my_pastes.html")
def show_my_pastes(user, count=8):
    my_pastes = Paste.objects.filter(author=user)[:count]
    return {"my_pastes": my_pastes}
