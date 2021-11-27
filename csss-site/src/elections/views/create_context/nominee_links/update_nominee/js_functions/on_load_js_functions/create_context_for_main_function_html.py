from elections.models import NomineeLink
from elections.views.Constants import NOMINEE_DIV__NAME, DRAFT_NOMINEE_HTML__NAME
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__NOMINEE, ELECTION_JSON_KEY__NOM_NAME, \
    ELECTION_JSON_KEY__NOM_FACEBOOK, ELECTION_JSON_KEY__NOM_LINKEDIN, ELECTION_JSON_KEY__NOM_EMAIL, \
    ELECTION_JSON_KEY__NOM_DISCORD
from elections.views.create_context.webform_format.create_context_for_display_nominee_info_html import \
    create_context_for_display_nominee_info_html


def create_context_for_main_function_html(
        context, nominee_link_id=None, create_new_nominee=False,
        nominee_info=None):
    context.update({
        NOMINEE_DIV__NAME: ELECTION_JSON_KEY__NOMINEE,
    })
    nominee_link = NomineeLink.objects.get(id=nominee_link_id)
    nominee_obj = nominee_link.nominee if nominee_link.nominee is not None else None

    if nominee_info is not None:
        context.update(
            {
                DRAFT_NOMINEE_HTML__NAME: {
                    ELECTION_JSON_KEY__NOM_NAME: nominee_info[ELECTION_JSON_KEY__NOM_NAME],
                    ELECTION_JSON_KEY__NOM_FACEBOOK: nominee_info[ELECTION_JSON_KEY__NOM_FACEBOOK],
                    ELECTION_JSON_KEY__NOM_LINKEDIN: nominee_info[ELECTION_JSON_KEY__NOM_LINKEDIN],
                    ELECTION_JSON_KEY__NOM_EMAIL: nominee_info[ELECTION_JSON_KEY__NOM_EMAIL],
                    ELECTION_JSON_KEY__NOM_DISCORD: nominee_info[ELECTION_JSON_KEY__NOM_DISCORD]
                }
            }
        )
    elif nominee_obj is not None:
        context.update(
            {
                DRAFT_NOMINEE_HTML__NAME: {
                    ELECTION_JSON_KEY__NOM_NAME: nominee_obj.name,
                    ELECTION_JSON_KEY__NOM_FACEBOOK: nominee_obj.facebook,
                    ELECTION_JSON_KEY__NOM_LINKEDIN: nominee_obj.linkedin,
                    ELECTION_JSON_KEY__NOM_EMAIL: nominee_obj.email,
                    ELECTION_JSON_KEY__NOM_DISCORD: nominee_obj.discord
                }
            }
        )
    create_context_for_display_nominee_info_html(
        context, nominee_obj=nominee_obj, nominee_info=nominee_info, include_id_for_nominee=False
    )
