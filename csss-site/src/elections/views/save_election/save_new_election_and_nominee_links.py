import datetime
import string
import random

from elections.models import NomineeLink
from elections.views.Constants import DATE_AND_TIME_FORMAT, \
    NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__ELECTION_TYPE, ELECTION_JSON_KEY__WEBSURVEY, \
    ELECTION_JSON_KEY__DATE, ELECTION_JSON_WEBFORM_KEY__TIME
from elections.views.extractors.get_election_slug_and_name import gete_slug_and_human_friendly_name_election
from elections.views.save_election.save_new_election_obj_jformat import create_and_save_election_object_jformat


def save_new_election_and_nominee_links(election_dict):
    election_type = election_dict[ELECTION_JSON_KEY__ELECTION_TYPE]
    election_websurvey = election_dict[ELECTION_JSON_KEY__WEBSURVEY]
    date_and_time = f"{election_dict[ELECTION_JSON_KEY__DATE]} " \
                    f"{election_dict[ELECTION_JSON_WEBFORM_KEY__TIME]}"
    election_date = datetime.datetime.strptime(
        date_and_time, DATE_AND_TIME_FORMAT
    )
    slug, human_friendly_name = gete_slug_and_human_friendly_name_election(election_date, election_type)
    election = create_and_save_election_object_jformat(election_type, election_websurvey, election_date, slug,
                                                       human_friendly_name)
    for nominee_link in election_dict[NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS].split("\r\n"):
        # creating the necessary passphrases and officer info for the user inputted position
        passphrase = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(10))
        while len(NomineeLink.objects.all().filter(passphrase=passphrase)) > 0:
            passphrase = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(10))
        NomineeLink(election=election, full_name=nominee_link, passphrase=passphrase).save()
    return election
