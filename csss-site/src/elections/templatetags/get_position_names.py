from django import template

register = template.Library()


@register.simple_tag
def get_position_names(position_names=None):
    if 'position_name' in position_names[0]:
        return [position_name['position_name'] for position_name in position_names]
    else:
        return [position_name.split("_")[0] for position_name in position_names]


@register.simple_tag
def get_position_id(position_name, position_names):
    if position_name not in get_position_names(position_names):
        return None
    for position_name_info in position_names:
        if 'position_name' in position_name_info:
            if position_name_info['position_name'] == position_name:
                return position_name_info['id']
        else:
            position_info = position_name_info.split("_")
            if len(position_info) > 1:
                if position_info[0] == position_name:
                    return
    return None


@register.simple_tag
def clear_variable():
    return ""
