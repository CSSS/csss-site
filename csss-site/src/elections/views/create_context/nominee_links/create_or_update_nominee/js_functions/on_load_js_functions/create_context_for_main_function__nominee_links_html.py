from elections.views.Constants import NOMINEE_DIV__NAME, DRAFT_NOMINEE_HTML__NAME
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__NOMINEE, ELECTION_JSON_KEY__NOM_NAME, \
    ELECTION_JSON_KEY__NOM_FACEBOOK, ELECTION_JSON_KEY__NOM_LINKEDIN, ELECTION_JSON_KEY__NOM_EMAIL, \
    ELECTION_JSON_KEY__NOM_DISCORD
from elections.views.create_context.webform_format.create_context_for_display_nominee_info_html import \
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
                    ELECTION_JSON_KEY__NOM_NAME: nominee_info[ELECTION_JSON_KEY__NOM_NAME],
                    ELECTION_JSON_KEY__NOM_FACEBOOK: nominee_info[ELECTION_JSON_KEY__NOM_FACEBOOK],
                    ELECTION_JSON_KEY__NOM_LINKEDIN: nominee_info[ELECTION_JSON_KEY__NOM_LINKEDIN],
                    ELECTION_JSON_KEY__NOM_EMAIL: nominee_info[ELECTION_JSON_KEY__NOM_EMAIL],
                    ELECTION_JSON_KEY__NOM_DISCORD: nominee_info[ELECTION_JSON_KEY__NOM_DISCORD]
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
                nominee_obj.name: {
                    ELECTION_JSON_KEY__NOM_NAME: nominee_obj.name,
                    ELECTION_JSON_KEY__NOM_FACEBOOK: nominee_obj.facebook,
                    ELECTION_JSON_KEY__NOM_LINKEDIN: nominee_obj.linkedin,
                    ELECTION_JSON_KEY__NOM_EMAIL: nominee_obj.email,
                    ELECTION_JSON_KEY__NOM_DISCORD: nominee_obj.discord
                }
            }
            create_context_for_display_nominee_info_html(
                context, draft_or_finalized_nominee_to_display=True,
                include_id_for_nominee=False, webform_election=False, new_webform_election=False,
                nominee_info_to_add_to_context=nominee_info_to_add_to_context,
                nominee_info=nominee_info, nominee_obj=nominee_obj,
                populate_nominee_info=True
            )
            context[DRAFT_NOMINEE_HTML__NAME] = nominee_info_to_add_to_context[nominee_obj.name]
    else:
        create_context_for_display_nominee_info_html(
            context, draft_or_finalized_nominee_to_display=False
        )
