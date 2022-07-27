import logging

from about.models import Term, NewOfficer, Officer, OfficerEmailListAndPositionMapping
from about.views.input_new_officers.discord_dms.dm_new_officers_on_discord import dm_new_officers_on_discord
from about.views.input_new_officers.specify_new_officers.determine_start_date import determine_start_date

logger = logging.getLogger('csss_site')


def save_new_officers(inputted_term, inputted_year, new_officers=None):
    """
    Saves the inputted officers with the specified term and year

    Keyword Arguments
    inputted_term -- the term that the new officers were voted in
    inputted_year -- the year that the new officers were voted in
    new_officers -- the new officers that the user has inputted

    Return
    bool -- indicates if the new officers were all successfully DMed
    error_message - the relevant error message if any of the new officers could not be DMed
    """
    if new_officers is None:
        new_officers = []
    if len(new_officers) == 0:
        return
    term = Term.objects.all().filter(term=inputted_term, year=inputted_year).first()
    if term is None:
        term = Term(term=inputted_term, year=inputted_year)
        term.save()
    saved_new_officers = {new_officer.id: new_officer for new_officer in NewOfficer.objects.all()}
    saved_new_officers_sfu_computer_ids = [
        saved_new_officer.sfu_computing_id for saved_new_officer in saved_new_officers.values()
    ]
    logger.info(f"[about/save_new_officers.py save_new_officers()] creating Map={saved_new_officers_sfu_computer_ids}")
    officer_email_list_and_position_mapping = OfficerEmailListAndPositionMapping.objects.all()
    officers = Officer.objects.all()
    for new_officer in new_officers:
        discord_id = None
        if len(new_officer['discord_id'].strip()) > 0:
            discord_id = new_officer['discord_id'].strip()
        sfu_computing_id = new_officer['sfu_computing_id'].strip()
        full_name = new_officer['full_name'].strip()
        position_name = new_officer['position_name'].strip()
        start_date = determine_start_date(
            officers,
            officer_email_list_and_position_mapping,
            're_use_start_date' in new_officer,
            new_officer['start_date'].strip(),
            sfu_computing_id, position_name
        )
        first_time_officer = officers.filter(sfuid=sfu_computing_id).first() is None
        logger.info(
            f"[about/save_new_officers.py save_new_officers()] saving officer with the following details:"
            f"\n\tposition_name={position_name}"
            f"\n\tdiscord_id={discord_id}"
            f"\n\tsfu_computing_id={sfu_computing_id}"
            f"\n\tstart_date={start_date}"
            f"\n\tterm={term}"
        )
        will_be_new_officer_obj = 'id' not in new_officer
        new_officer_obj = NewOfficer() if will_be_new_officer_obj else NewOfficer.objects.get(id=new_officer['id'])
        new_officer_obj.full_name = full_name
        new_officer_obj.position_name = position_name
        new_officer_obj.discord_id = discord_id
        new_officer_obj.sfu_computing_id = sfu_computing_id
        new_officer_obj.start_date = start_date
        new_officer_obj.term = term
        new_officer_obj.re_use_start_date = 're_use_start_date' in new_officer
        new_officer_obj.overwrite_current_officer = 'overwrite_current_officer' in new_officer
        new_officer_obj.save()
        if new_officer_obj.id in saved_new_officers:
            del saved_new_officers[new_officer_obj.id]
            logger.info(
                f"[about/save_new_officers.py save_new_officers()] removed {sfu_computing_id} "
                "from the map of new officers to delete"
            )
        if will_be_new_officer_obj:
            success, error_message = dm_new_officers_on_discord(full_name, discord_id, first_time_officer)
            if not success:
                return success, error_message
    for new_officer in saved_new_officers.values():
        logger.info(f"[about/save_new_officers.py save_new_officers()] deleting NewOfficer ({new_officer.sfu_computing_id})#{new_officer.id}")
        new_officer.delete()
    return True, None
