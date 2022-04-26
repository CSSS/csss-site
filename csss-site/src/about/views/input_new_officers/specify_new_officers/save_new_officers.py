import logging

from about.models import Term, NewOfficer
from about.views.input_new_officers.specify_new_officers.determine_start_date import determine_start_date

logger = logging.getLogger('csss_site')


def save_new_officers(new_officers_dict):
    inputted_term = new_officers_dict['term']
    inputted_year = new_officers_dict['year']
    term = Term.objects.all().filter(term=inputted_term, year=inputted_year).first()
    if term is None:
        term = Term(term=inputted_term, year=inputted_year)
        term.save()
    for new_officer in new_officers_dict['new_officers']:
        discord_id = None
        if len(new_officer['discord_id'].strip()) > 0:
            discord_id = new_officer['discord_id'].strip()
        sfu_computing_id = new_officer['sfu_computing_id'].strip()
        full_name = new_officer['full_name'].strip()
        position_name = new_officer['position_name'].strip()
        start_date = determine_start_date(
            're_use_start_date' in new_officer,
            new_officer['start_date'].strip(),
            sfu_computing_id, position_name
        )
        logger.info(
            f"[about/save_new_officers.py save_new_officers()] saving officer with the following details:"
            f"\n\tposition_name={position_name}"
            f"\n\tdiscord_id={discord_id}"
            f"\n\tsfu_computing_id={sfu_computing_id}"
            f"\n\tstart_date={start_date}"
            f"\n\tterm={term}"
        )
        if 'id' in new_officer:
            new_officer_obj = NewOfficer.objects.get(id=new_officer['id'])
        else:
            new_officer_obj = NewOfficer()
        new_officer_obj.full_name = full_name
        new_officer_obj.position_name = position_name
        new_officer_obj.discord_id = discord_id
        new_officer_obj.sfu_computing_id = sfu_computing_id
        new_officer_obj.start_date = start_date
        new_officer_obj.term = term
        new_officer_obj.re_use_start_date = 're_use_start_date' in new_officer
        new_officer_obj.overwrite_current_officer = 'overwrite_current_officer' in new_officer
        new_officer_obj.save()
