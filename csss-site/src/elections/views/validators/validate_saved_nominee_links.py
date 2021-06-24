from elections.models import NomineeLink, Nominee
from elections.views.Constants import SAVED_NOMINEE_LINK__ID, SAVED_NOMINEE_LINK__NAME, SAVED_NOMINEE_LINK__NOMINEE, \
    DELETE, NO_NOMINEE_LINKED


def validate_saved_nominee_links(nominee_links):
    if type(nominee_links) != list:
        return False, "Did not receive a list of nominee links"
    linked_nominees = []
    for nominee_link in nominee_links:
        if not (
                SAVED_NOMINEE_LINK__ID in nominee_link and SAVED_NOMINEE_LINK__NAME in nominee_link and
                SAVED_NOMINEE_LINK__NOMINEE in nominee_link
        ):
            return False, f"It seems that one of the following fields is missing for a nominee link: " \
                          f" {SAVED_NOMINEE_LINK__ID}, {SAVED_NOMINEE_LINK__NAME}, " \
                          f"{SAVED_NOMINEE_LINK__NOMINEE}"
        nominee_link_id = nominee_link[SAVED_NOMINEE_LINK__ID]
        if len(NomineeLink.objects.all().filter(id=nominee_link_id)) != 1:
            return False, f"Invalid Nominee Link Id of {nominee_link_id} passed for one of the nominee links"
        if DELETE in nominee_link and nominee_link[DELETE] != "True":
            return False, f"Unable to understand a delete command of {nominee_link[DELETE]}"
        linked_nominee_id = nominee_link[SAVED_NOMINEE_LINK__NOMINEE]
        marked_for_deletion = DELETE in nominee_link and nominee_link[DELETE] == "True"
        if not marked_for_deletion:
            if linked_nominee_id != NO_NOMINEE_LINKED:
                if len(Nominee.objects.all().filter(id=linked_nominee_id)) != 1:
                    return False, f"Invalid Nominee id of {linked_nominee_id} was detected"
                else:
                    if linked_nominee_id in linked_nominees:
                        return False, "More than 1 Nominee Link was assigned to the same nominee of " \
                                      f"{Nominee.objects.get(id=linked_nominee_id)}"
                    linked_nominees.append(linked_nominee_id)
    return True, None
