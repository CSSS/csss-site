from django import template

from elections.templatetags.get_position_names import get_position_names
from elections.views.Constants import ELECTION_JSON_KEY__NOM_POSITION_NAME, ID_KEY

register = template.Library()


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
        if ELECTION_JSON_KEY__NOM_POSITION_NAME in position_info:
            if position_info[ELECTION_JSON_KEY__NOM_POSITION_NAME] == position_name:
                return position_info[ID_KEY]
    return None
