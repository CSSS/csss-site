import random
import string

from elections.models import NomineeLink, Nominee
from elections.views.Constants import SAVED_NOMINEE_LINK__ID, SAVED_NOMINEE_LINK__NAME, SAVED_NOMINEE_LINK__NOMINEE, \
    DELETE, NO_NOMINEE_LINKED


def update_existing_nominee_links_from_jformat(election, saved_nominee_links, new_nominee_names):
    if new_nominee_names is not None:
        for new_nominee_name in new_nominee_names.split("\r\n"):
            if new_nominee_name.strip() != "":
                new_nominee_name = new_nominee_name.strip()
                # creating the necessary passphrases and officer info for the user inputted position
                passphrase = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(10))
                while len(NomineeLink.objects.all().filter(passphrase=passphrase)) > 0:
                    passphrase = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(10))
                NomineeLink(election=election, name=new_nominee_name, passphrase=passphrase).save()
    if saved_nominee_links is not None:
        for saved_nominee_link in saved_nominee_links:
            nominee_link = NomineeLink.objects.get(id=int(saved_nominee_link[SAVED_NOMINEE_LINK__ID]))
            marked_for_deletion = DELETE in saved_nominee_link and saved_nominee_link[DELETE] == "True"
            if marked_for_deletion:
                nominee_link.delete()
            else:
                nominee_link.name = saved_nominee_link[SAVED_NOMINEE_LINK__NAME]
                if saved_nominee_link[SAVED_NOMINEE_LINK__NOMINEE] != NO_NOMINEE_LINKED:
                    nominee_link.nominee = Nominee.objects.get(id=int(saved_nominee_link[SAVED_NOMINEE_LINK__NOMINEE]))
                else:
                    nominee_link.nominee = None
                nominee_link.save()
