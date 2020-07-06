from django import template

from elections.models import NominationPage

register = template.Library()


@register.simple_tag
def get_nom_pages():
    nom_pages = NominationPage.objects.all()
    if len(nom_pages) == 0:
        return None
    return nom_pages
