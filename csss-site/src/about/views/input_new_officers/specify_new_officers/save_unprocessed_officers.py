from about.models import Term, UnProcessedOfficer
from about.views.Constants import DISCORD_ID_KEY, SFU_COMPUTING_ID_KEY, FULL_NAME_KEY, \
    RE_USE_START_DATE_KEY, START_DATE_KEY, POSITION_NAME_KEY, OVERWRITE_CURRENT_OFFICER_KEY, ID_KEY
from about.views.input_new_officers.specify_new_officers.notifications. \
    send_notification_asking_officer_to_fill_in_form import \
    send_notification_asking_officer_to_fill_in_form
from about.views.input_new_officers.specify_new_officers.utils.determine_start_date import determine_start_date
from csss.setup_logger import Loggers


def save_unprocessed_officers(saved_unprocessed_officers, officer_emaillist_and_position_mappings, officers, terms,
                              inputted_term, inputted_year, unprocessed_officers=None):
    """
    Saves the inputted officers with the specified term and year

    Keyword Arguments
    saved_unprocessed_officers -- the queryset of currently saved unprocessed officers
    officer_emaillist_and_position_mappings -- the queryset of currently saved position infos
    officers -- the queryset of currently saved officers
    terms -- the queryset of currently saved terms
    inputted_term -- the term that the unprocessed officers were voted in
    inputted_year -- the year that the unprocessed officers were voted in
    unprocessed_officers -- the unprocessed officers that the user has inputted

    Return
    bool -- indicates if the unprocessed officers were all successfully DMed
    error_message - the relevant error message if any of the unprocessed officers could not be DMed
    """
    logger = Loggers.get_logger()
    if unprocessed_officers is None:
        unprocessed_officers = []
    if len(unprocessed_officers) == 0:
        return False, "No officers detected in response"
    term = terms.filter(term=inputted_term, year=int(inputted_year)).first()
    if term is None:
        term = Term(term=inputted_term, year=int(inputted_year))
        term.save()
    saved_unprocessed_officers_dict = {
        unprocessed_officer.id: unprocessed_officer for unprocessed_officer in saved_unprocessed_officers
    }
    saved_unprocessed_officers_sfu_computer_ids = [
        saved_unprocessed_officer.sfu_computing_id
        for saved_unprocessed_officer in saved_unprocessed_officers_dict.values()
    ]
    logger.info(
        f"[about/save_unprocessed_officers.py save_unprocessed_officers()] "
        f"creating Map={saved_unprocessed_officers_sfu_computer_ids}"
    )
    for unprocessed_officer in unprocessed_officers:
        discord_id = None
        if len(unprocessed_officer[DISCORD_ID_KEY].strip()) > 0:
            discord_id = unprocessed_officer[DISCORD_ID_KEY].strip()
        sfu_computing_id = unprocessed_officer[SFU_COMPUTING_ID_KEY].strip()
        full_name = unprocessed_officer[FULL_NAME_KEY].strip()
        position_name = unprocessed_officer[POSITION_NAME_KEY].strip()
        start_date = determine_start_date(
            officers,
            officer_emaillist_and_position_mappings,
            RE_USE_START_DATE_KEY in unprocessed_officer,
            unprocessed_officer[START_DATE_KEY].strip(),
            sfu_computing_id, position_name, term
        )
        first_time_officer = officers.filter(sfu_computing_id=sfu_computing_id).first() is None
        logger.info(
            f"[about/save_unprocessed_officers.py save_unprocessed_officers()] "
            f"saving officer with the following details:"
            f"\n\tposition_name={position_name}"
            f"\n\tdiscord_id={discord_id}"
            f"\n\tsfu_computing_id={sfu_computing_id}"
            f"\n\tstart_date={start_date}"
            f"\n\tterm={term}"
        )
        will_be_new_unprocessed_officer_obj = ID_KEY not in unprocessed_officer
        unprocessed_officer_obj = UnProcessedOfficer() \
            if will_be_new_unprocessed_officer_obj \
            else saved_unprocessed_officers.filter(id=unprocessed_officer[ID_KEY]).first()
        unprocessed_officer_obj.full_name = full_name
        unprocessed_officer_obj.position_name = position_name
        unprocessed_officer_obj.discord_id = discord_id
        unprocessed_officer_obj.sfu_computing_id = sfu_computing_id
        unprocessed_officer_obj.start_date = start_date
        unprocessed_officer_obj.term = term
        unprocessed_officer_obj.re_use_start_date = RE_USE_START_DATE_KEY in unprocessed_officer
        unprocessed_officer_obj.overwrite_current_officer = False
        unprocessed_officer_obj.save()
        if unprocessed_officer_obj.id in saved_unprocessed_officers_dict:
            del saved_unprocessed_officers_dict[unprocessed_officer_obj.id]
            logger.info(
                f"[about/save_unprocessed_officers.py save_unprocessed_officers()] removed {sfu_computing_id} "
                "from the map of unprocessed officers to delete"
            )
        if will_be_new_unprocessed_officer_obj:
            success, error_message = send_notification_asking_officer_to_fill_in_form(
                discord_id, full_name, first_time_officer
            )
            if not success:
                return success, error_message
    for unprocessed_officer in saved_unprocessed_officers_dict.values():
        logger.info(f"[about/save_unprocessed_officers.py save_unprocessed_officers()] "
                    f"deleting UnProcessedOfficer ({unprocessed_officer.sfu_computing_id})#{unprocessed_officer.id}")
        unprocessed_officer.delete()
    return True, None
