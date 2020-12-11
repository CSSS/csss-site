import logging

from querystring_parser import parser

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


