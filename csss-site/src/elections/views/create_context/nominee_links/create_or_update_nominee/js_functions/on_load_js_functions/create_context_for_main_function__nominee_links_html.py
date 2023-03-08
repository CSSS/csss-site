from elections.views.Constants import NOMINEE_DIV__NAME, DRAFT_NOMINEE_HTML__NAME, NA_STRING
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__NOMINEE, ELECTION_JSON_KEY__NOM_NAME, \
    ELECTION_JSON_KEY__NOM_FACEBOOK, ELECTION_JSON_KEY__NOM_LINKEDIN, ELECTION_JSON_KEY__NOM_EMAIL, \
    ELECTION_JSON_KEY__NOM_INSTAGRAM, ELECTION_JSON_KEY__NOM_DISCORD_ID, ELECTION_JSON_KEY__NOM_SFUID
from elections.views.create_context.webform_format.js_functions.on_load_js_function.\
    create_context_for_display_nominee_info_html import \
    create_context_for_display_nominee_info_html


def create_context_for_main_function__nominee_links_html(context, nominee_info=None, nominee_obj=None):
    """
    populates the context dictionary that is used by
     elections/templates/elections/nominee_links/create_or_update_nominee/js_functions/
     on_load_js_functions/main_function__nominee_links.html

    Keyword Arguments
    context -- the context dictionary that has to be populated for the main_function.html
    nominee_info -- the nominee info that the user inputted, otherwise None
    nominee_obj -- the object that contains the saved nominee info
    """
    context.update({
        NOMINEE_DIV__NAME: ELECTION_JSON_KEY__NOMINEE,
    })
    if nominee_info is not None or nominee_obj is not None:
        if nominee_info is not None:
            nominee_info_to_add_to_context = {
                ELECTION_JSON_KEY__NOM_NAME: nominee_info.get(ELECTION_JSON_KEY__NOM_NAME, NA_STRING),
                ELECTION_JSON_KEY__NOM_SFUID: nominee_info.get(ELECTION_JSON_KEY__NOM_SFUID, NA_STRING),
                ELECTION_JSON_KEY__NOM_FACEBOOK: nominee_info.get(ELECTION_JSON_KEY__NOM_FACEBOOK, NA_STRING),
                ELECTION_JSON_KEY__NOM_INSTAGRAM: nominee_info.get(ELECTION_JSON_KEY__NOM_INSTAGRAM, NA_STRING),
                ELECTION_JSON_KEY__NOM_LINKEDIN: nominee_info.get(ELECTION_JSON_KEY__NOM_LINKEDIN, NA_STRING),
                ELECTION_JSON_KEY__NOM_EMAIL: nominee_info.get(ELECTION_JSON_KEY__NOM_EMAIL, NA_STRING),
                ELECTION_JSON_KEY__NOM_DISCORD_ID: nominee_info.get(ELECTION_JSON_KEY__NOM_DISCORD_ID, NA_STRING)

            }
            create_context_for_display_nominee_info_html(
                context, draft_or_finalized_nominee_to_display=True,
                include_id_for_nominee=False, webform_election=False, new_webform_election=False,
                nominee_info_to_add_to_context=nominee_info_to_add_to_context,
                nominee_info=nominee_info, nominee_obj=nominee_obj,
                populate_nominee_info=True
            )
            context[DRAFT_NOMINEE_HTML__NAME] = nominee_info_to_add_to_context
        elif nominee_obj is not None:
            nominee_info_to_add_to_context = {
                nominee_obj.full_name: {
                    ELECTION_JSON_KEY__NOM_NAME: nominee_obj.get_full_name,
                    ELECTION_JSON_KEY__NOM_SFUID: nominee_obj.get_sfuid,
                    ELECTION_JSON_KEY__NOM_FACEBOOK: nominee_obj.get_facebook,
                    ELECTION_JSON_KEY__NOM_INSTAGRAM: nominee_obj.get_instagram,
                    ELECTION_JSON_KEY__NOM_LINKEDIN: nominee_obj.get_linkedin,
                    ELECTION_JSON_KEY__NOM_EMAIL: nominee_obj.get_email,
                    ELECTION_JSON_KEY__NOM_DISCORD_ID: nominee_obj.get_discord_id
                }
            }
            create_context_for_display_nominee_info_html(
                context, draft_or_finalized_nominee_to_display=True,
                include_id_for_nominee=False, webform_election=False, new_webform_election=False,
                nominee_info_to_add_to_context=nominee_info_to_add_to_context,
                nominee_info=nominee_info, nominee_obj=nominee_obj,
                populate_nominee_info=True
            )
            context[DRAFT_NOMINEE_HTML__NAME] = nominee_info_to_add_to_context[nominee_obj.full_name]
    else:
        create_context_for_display_nominee_info_html(
            context, draft_or_finalized_nominee_to_display=False
        )
