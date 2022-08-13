from elections.models import NomineeLink, Nominee
from elections.views.Constants import SAVED_NOMINEE_LINK__ID, SAVED_NOMINEE_LINK__NAME, SAVED_NOMINEE_LINK__NOMINEE, \
    DELETE, NO_NOMINEE_LINKED


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
                nominee_link.full_name = saved_nominee_link[SAVED_NOMINEE_LINK__NAME]
                if saved_nominee_link[SAVED_NOMINEE_LINK__NOMINEE] != NO_NOMINEE_LINKED:
                    nominee_link.nominee = Nominee.objects.get(
                        id=int(saved_nominee_link[SAVED_NOMINEE_LINK__NOMINEE])
                    )
                else:
                    nominee_link.nominee = None
                nominee_link.save()
