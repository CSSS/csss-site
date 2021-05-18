from django import template

register = template.Library()


@register.simple_tag
def clear_variable():
    """
    Clears the variable by returning ""
    """
    return ""
