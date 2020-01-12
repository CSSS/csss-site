from django import template

from about.models import Term

register = template.Library()


@register.simple_tag
def get_specific_term():
    return list(reversed(Term.objects.all()))
