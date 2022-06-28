import logging

from about.models import Term, NewOfficer
from about.views.input_new_officers.discord_dms.dm_new_officers_on_discord import dm_new_officers_on_discord
from about.views.input_new_officers.specify_new_officers.determine_start_date import determine_start_date

logger = logging.getLogger('csss_site')


def save_new_officers(inputted_term, inputted_year, new_officers=None):
    if new_officers is None:
        new_officers = []
    if len(new_officers) == 0:
        return
    term = Term.objects.all().filter(term=inputted_term, year=inputted_year).first()
    if term is None:
        term = Term(term=inputted_term, year=inputted_year)
        term.save()
    saved_new_officers = {new_officer.sfu_computing_id: new_officer for new_officer in NewOfficer.objects.all()}
    for new_officer in new_officers:
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
        if sfu_computing_id in saved_new_officers:
            del saved_new_officers[sfu_computing_id]
        new_officer_obj.save()
        dm_new_officers_on_discord(full_name, discord_id)
    for new_officer in saved_new_officers.values():
        new_officer.delete()
