from django import template

from about.models import Term

register = template.Library()

@register.simple_tag
def get_specificTerm():
	return list(reversed(Term.objects.all()))
