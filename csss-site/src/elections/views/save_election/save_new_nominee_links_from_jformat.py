import random
import string

from elections.models import NomineeLink


def save_new_nominee_links_from_jformat(election, new_nominee_sfuids):
    """
    save new nominee links

    Keyword Arguments
    election -- the election object to save the new nominee links to
    new_nominee_sfuids -- the SFU IDs of the nominees that links have to be created for
    """
    if new_nominee_sfuids is not None and type(new_nominee_sfuids) == str:
        for new_nominee_sfuid in new_nominee_sfuids.split("\r\n"):
            if new_nominee_sfuid.strip() != "":
                new_nominee_sfuid = new_nominee_sfuid.strip()
                passphrase = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(10))
                while len(NomineeLink.objects.all().filter(passphrase=passphrase)) > 0:
                    passphrase = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(10))
                NomineeLink(election=election, sfuid=new_nominee_sfuid, passphrase=passphrase).save()
