from about.views.input_new_officers.enter_new_officer_info.utils.get_sfu_info import get_sfu_info
from elections.models import NomineeLink, Nominee
from elections.views.Constants import SAVED_NOMINEE_LINK__ID, SAVED_NOMINEE_LINK__NOMINEE, \
    DELETE, NO_NOMINEE_LINKED, SAVED_NOMINEE_LINK__SFUID, SAVED_NOMINEE_LINK__DISCORD_ID, NA_STRING


def update_existing_nominee_links_from_jformat(saved_nominee_links):
    """
    updates existing nominee links

    Keyword Argument
    saved_nominee_links -- the list of saved nominee links that need to be updated or deleted
    """
    if saved_nominee_links is not None and type(saved_nominee_links) == list:
        for saved_nominee_link in saved_nominee_links:
            nominee_link = NomineeLink.objects.get(id=int(saved_nominee_link[SAVED_NOMINEE_LINK__ID]))
            marked_for_deletion = DELETE in saved_nominee_link and saved_nominee_link[DELETE] == "True"
            if marked_for_deletion:
                nominee_link.delete()
            else:
                nominee_link.sfuid = saved_nominee_link[SAVED_NOMINEE_LINK__SFUID].strip()
                nominee_link.discord_id = saved_nominee_link[SAVED_NOMINEE_LINK__DISCORD_ID].strip()
                success, error_message, sfu_info = get_sfu_info(nominee_link.sfuid)
                nominee_link.full_name = f"{sfu_info['firstnames']} {sfu_info['lastname']}" if success else NA_STRING
                if saved_nominee_link[SAVED_NOMINEE_LINK__NOMINEE] != NO_NOMINEE_LINKED:
                    nominee_link.nominee = Nominee.objects.get(
                        id=int(saved_nominee_link[SAVED_NOMINEE_LINK__NOMINEE])
                    )
                else:
                    nominee_link.nominee = None
                nominee_link.save()
