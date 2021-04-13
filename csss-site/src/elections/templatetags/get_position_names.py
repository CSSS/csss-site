from django import template

from elections.views.Constants import NOM_POSITION_KEY, NOM_ID_KEY

register = template.Library()


@register.simple_tag
def get_position_names(position_infos=None):
    """
    Takes in an array whose elements are dicts with the key 'position_name' and returns a list of just those values

    Keyword Argument
    position_infos -- an array of dicts which has both position names and position IDs

    Return
    a list of the position names, or an empty list of position_names is None
    """
    if NOM_POSITION_KEY in position_infos[0]:
        return [position_name[NOM_POSITION_KEY] for position_name in position_infos]
    return []


@register.simple_tag
def get_position_id(position_name, position_infos):
    """
    Gets the ID for a position name

    Keyword Argument
    position_name -- the position name whose ID is returned
    position_infos -- an array of dicts which has both position names and position IDs

    Returns
    the ID of the position_name, if found. Otherwise None
    """
    if position_name not in get_position_names(position_infos):
        return None
    for position_info in position_infos:
        if NOM_POSITION_KEY in position_info:
            if position_info[NOM_POSITION_KEY] == position_name:
                return position_info[NOM_ID_KEY]
    return None


@register.simple_tag
def clear_variable():
    """
    Clears the variable by returning ""
    """
    return ""
