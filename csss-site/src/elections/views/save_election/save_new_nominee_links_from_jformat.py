import random
import string

from elections.models import NomineeLink


def save_new_nominee_links_from_jformat(election, new_nominee_names):
    """
    save new nominee links

    Keyword Arguments
    election -- the election object to save the new nominee links to
    new_nominee_names -- the nominee names that links have to be created for
    """
    if new_nominee_names is not None and type(new_nominee_names) == str:
        for new_nominee_name in new_nominee_names.split("\r\n"):
            if new_nominee_name.strip() != "":
                new_nominee_name = new_nominee_name.strip()
                passphrase = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(10))
                while len(NomineeLink.objects.all().filter(passphrase=passphrase)) > 0:
                    passphrase = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(10))
                NomineeLink(election=election, name=new_nominee_name, passphrase=passphrase).save()