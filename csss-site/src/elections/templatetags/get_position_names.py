from django import template

from elections.views.Constants_v2 import ELECTION_JSON_KEY__NOM_POSITION_NAME

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
    if ELECTION_JSON_KEY__NOM_POSITION_NAME in position_infos[0]:
        return [position_name[ELECTION_JSON_KEY__NOM_POSITION_NAME] for position_name in position_infos]
    return []