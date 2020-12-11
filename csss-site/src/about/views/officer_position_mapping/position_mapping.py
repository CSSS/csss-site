import logging

from querystring_parser import parser

from about.models import OfficerEmailListAndPositionMapping
from about.views.officer_management_helper import TAB_STRING
from about.views.officer_position_mapping.add_new_position_mapping import add_new_position_mapping
from about.views.officer_position_mapping.display_position_mapping_html import display_position_mapping_html
from about.views.officer_position_mapping.update_existing_position_mapping import modify_existing_position_mapping
from csss.Constants import Constants
from csss.views_helper import verify_access_logged_user_and_create_context, ERROR_MESSAGE_KEY

logger = logging.getLogger('csss_site')


def position_mapping(request):
    """
    Handles any modifications done to position mappings
    """
    logger.info(f"[about/position_mapping.py position_mapping()] request.POST={request.POST}")
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request,
                                                                                          TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = f'{error_message}<br>'
        return render_value

    if request.method != "POST":
        return display_position_mapping_html(request, context)
    post_dict = parser.parse(request.POST.urlencode())
    if Constants.user_select_to_a_position_mapping_option in post_dict:  # modifying an existing position mapping
        return modify_existing_position_mapping(request, context, post_dict)
    else:  # adding new position mapping[s]
        return add_new_position_mapping(request, context, post_dict)


def validate_position_index(position_index, submitted_position_indexes=None):
    """
    Validates the new inputted position index

    Keyword Argument
    position_index -- the new position index
    submitted_position_indexes -- other indexes specified by the user so far
     if they are submitting multiple positions at once

    Return
    success -- True or False if the new position index is not already used
    error_message -- an error_message if the index was already used
    """
    if submitted_position_indexes is None:
        submitted_position_indexes = []
    if len(OfficerEmailListAndPositionMapping.objects.all().filter(
            position_index=position_index)) > 0 or position_index in submitted_position_indexes:
        logger.info(f"[about/position_mapping.py validate_position_index()] validate for position index "
                    f"{position_index} was unsuccessful")
        return False, f"Another Position already has an index of {position_index}"
    logger.info(f"[about/position_mapping.py validate_position_index()] validate for position index "
                f"{position_index} was successful")
    return True, None


def validate_position_name(position_name, submitted_position_names=None):
    """
    Validates the new inputted position name

    Keyword Argument
    position_name -- the new position name
    submitted_position_names -- other names specified by the user so far if they
     are submitting multiple positions at once

    Return
    success -- True or False if the new position name is not already used
    error_message -- an error_message if the name was already used
    """
    if submitted_position_names is None:
        submitted_position_names = []
    if len(OfficerEmailListAndPositionMapping.objects.all().filter(
            position_name=position_name)) > 0 or position_name in submitted_position_names:
        logger.info(f"[about/position_mapping.py validate_position_name()] validate for position name "
                    f"{position_name} was unsuccessful")
        return False, f"the position of {position_name} already exists"
    logger.info(f"[about/position_mapping.py validate_position_name()] validate for position name "
                f"{position_name} was successful")
    return True, None
