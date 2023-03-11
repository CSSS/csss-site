import random
import string

from elections.models import NomineeLink
from elections.views.Constants import NA_STRING


def save_new_nominee_links_from_jformat(election, new_nominee_sfuids_and_discord_ids):
    """
    save new nominee links

    Keyword Arguments
    election -- the election object to save the new nominee links to
    new_nominee_sfuids_and_discord_ids -- the SFU IDs and Discord IDs of the nominees
     that links have to be created for
    """
    if new_nominee_sfuids_and_discord_ids is not None and type(new_nominee_sfuids_and_discord_ids) == str:
        for new_nominee_sfuids_and_discord_id in new_nominee_sfuids_and_discord_ids.split("\r\n"):
            if new_nominee_sfuids_and_discord_id.strip() != "":
                new_nominee_sfuid = new_nominee_sfuids_and_discord_id.split(",")[0].strip()
                new_nominee_discord_id = new_nominee_sfuids_and_discord_id.split(",")[1].strip()
                new_nominee_discord_id = new_nominee_discord_id if new_nominee_discord_id != NA_STRING else None
                passphrase = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(10))
                while len(NomineeLink.objects.all().filter(passphrase=passphrase)) > 0:
                    passphrase = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(10))
                NomineeLink(
                    election=election, sfuid=new_nominee_sfuid, discord_id=new_nominee_discord_id,
                    passphrase=passphrase
                ).save()
