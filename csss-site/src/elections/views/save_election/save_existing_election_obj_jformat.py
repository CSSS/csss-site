import datetime

from elections.views.extractors.get_election_slug_and_name import gete_slug_and_human_friendly_name_election


def update_existing_election_obj_from_jformat(election, date, election_type, websurvey_link):
    """
    updates the election info

    Keyword Argument:
    election -- the Election object to update
    date -- the new day of the election
    election_type -- the updated election type
    websurvey_link -- the updated link to the websurvey
    """
    election.date = datetime.datetime.strptime(f"{date}", DATE_AND_TIME_FORMAT)
    election.slug, election.human_friendly_name = \
        gete_slug_and_human_friendly_name_election(election.date, election_type)
    election.election_type = election_type
    election.websurvey = websurvey_link
    election.save()
