from django import template

from elections.models import NominationPage

register = template.Library()


@register.simple_tag
def get_nom_pages():
    return NominationPage.objects.all()
