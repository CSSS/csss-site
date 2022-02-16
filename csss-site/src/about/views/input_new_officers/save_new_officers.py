import datetime

from about.models import Term, NewOfficer
from about.views.input_new_officers.determine_start_date import determine_start_date


def save_new_officers(new_officers_dict):
    term = new_officers_dict['term']
    year = new_officers_dict['year']
    term = Term.objects.all().filter(term=term, year=year).first()
    for new_officer in new_officers_dict['new_officers']:
        discord_id = None
        if len(new_officer['discord_id'].strip()) > 0:
            discord_id = new_officer['discord_id'].strip()
        sfu_computing_id = new_officer['sfu_computing_id']
        start_date = datetime.datetime.now()
        position_name = new_officer['selected_position']
        if 'start_date' in new_officer:
            start_date = new_officer['start_date']
        NewOfficer(
            position_name=position_name, discord_id=discord_id, sfu_computing_id=sfu_computing_id,
            start_date=determine_start_date(start_date, sfu_computing_id, position_name)
            if 're_use_start_date' in new_officer else start_date, term=term
        ).save()
