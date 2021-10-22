from elections.views.Constants import CREATE_OR_UPDATE_VIA_NOMINEE_LINK__HTML_NAME


def create_context_for_display_nominee_info_html(context, include_id_for_nominee=True):
    context[CREATE_OR_UPDATE_VIA_NOMINEE_LINK__HTML_NAME] = include_id_for_nominee
