from django.shortcuts import render
from querystring_parser import parser

from about.models import OfficerEmailListAndPositionMapping, Term, Officer
from about.views.Constants import TAB_STRING
from about.views.position_mapping_helper import update_context, OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ID, \
    OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_INDEX, OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_NAME, \
    OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__EMAIL_LIST_ADDRESS, \
    OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ELECTED_VIA_ELECTION_OFFICER, \
    OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__NUMBER_OF_TERMS, \
    OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__STARTING_MONTH, \
    OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__GITHUB_ACCESS, \
    OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__GOOGLE_DRIVE_ACCESS, \
    OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__DISCORD_ROLE_NAME, \
    OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__EXECUTIVE_OFFICER, \
    OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ELECTION_OFFICER, \
    OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__SFSS_COUNCIL_REP, \
    OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__FROSH_WEEK_CHAIR, \
    OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__DISCORD_MANAGER
from csss.setup_logger import get_logger
from csss.views.context_creation.create_authenticated_contexts import create_context_for_updating_position_mappings
from csss.views.views import ERROR_MESSAGES_KEY
from csss.views_helper import get_current_term, get_datetime_for_beginning_of_current_term
from elections.models import NomineePosition

DELETE_POSITION_MAPPING_KEY = 'delete_position_mapping'
UN_DELETED_POSITION_MAPPING_KEY = 'un_delete_position_mapping'
UPDATE_POSITION_MAPPING_KEY = 'update_position_mapping'

logger = get_logger()


def update_saved_position_mappings(request):
    context = create_context_for_updating_position_mappings(request, tab=TAB_STRING)

    if request.method == "POST":
        context[ERROR_MESSAGES_KEY] = _update_positions_mapping(
            list(
                parser.parse(
                    request.POST.urlencode()
                )['saved_officer_positions'].values()
            )
        )
    return render(request, 'about/officer_positions/officer_positions.html', update_context(context))


def _update_positions_mapping(positions):
    """
    Updates the position mapping for the specified position

    Keyword Argument
    position -- the dict for a specific position

    Return
    error_messages -- a list of all the possible error messages
    """
    current_specified_position_names = []
    current_specified_position_indices = []
    positions_to_save = []
    nominees_to_save = []

    for position in positions:
        if not (OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ID in position
                and f"{position[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ID]}".isdigit()
                and len(
                OfficerEmailListAndPositionMapping.objects.all().filter(
                    id=int(position[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ID])
                )) > 0):
            error_message = "No valid position mapping id detected"
            logger.info(f"[about/update_saved_position_mappings.py _update_position_mapping()] {error_message}")
            return [error_message]
        if not (OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_INDEX in position
                and f"{position[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_INDEX]}".isdigit()):
            error_message = "No valid position index detected for position mapping"
            logger.info(f"[about/update_saved_position_mappings.py _update_position_mapping()] {error_message}")
            return [error_message]
        if not (OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_NAME in position):
            error_message = "No valid position name detected for position mapping"
            logger.info(f"[about/update_saved_position_mappings.py _update_position_mapping()] {error_message}")
            return [error_message]
        if not (OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__EMAIL_LIST_ADDRESS in position):
            error_message = "No valid position email list detected for position mapping"
            logger.info(f"[about/update_saved_position_mappings.py _update_position_mapping()] {error_message}")
            return [error_message]
        if not (OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__DISCORD_ROLE_NAME in position):
            error_message = "No valid position discord role name detected for position mapping"
            logger.info(f"[about/update_saved_position_mappings.py _update_position_mapping()] {error_message}")
            return [error_message]
        if not (OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__GITHUB_ACCESS in position):
            error_message = "No valid github access detected for position mapping"
            logger.info(f"[about/update_saved_position_mappings.py _update_position_mapping()] {error_message}")
            return [error_message]
        if not (OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__GOOGLE_DRIVE_ACCESS in position):
            error_message = "No valid google drive access detected for position mapping"
            logger.info(f"[about/update_saved_position_mappings.py _update_position_mapping()] {error_message}")
            return [error_message]
        if not (OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ELECTED_VIA_ELECTION_OFFICER in position):
            error_message = "No valid position elected status detected for position mapping"
            logger.info(f"[about/update_saved_position_mappings.py _update_position_mapping()] {error_message}")
            return [error_message]
        if not (OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__EXECUTIVE_OFFICER in position):
            error_message = "No valid indicator of whether position is an executive officer" \
                            " detected for position mapping"
            logger.info(f"[about/update_saved_position_mappings.py _update_position_mapping()] {error_message}")
            return [error_message]
        if not (OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ELECTION_OFFICER in position):
            error_message = "No valid indicator of whether position is for an election officer " \
                            "detected for position mapping"
            logger.info(f"[about/update_saved_position_mappings.py _update_position_mapping()] {error_message}")
            return [error_message]
        if not (OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__SFSS_COUNCIL_REP in position):
            error_message = "No valid indicator of whether position is for the SFSS council Rep " \
                            "detected for position mapping"
            logger.info(f"[about/update_saved_position_mappings.py _update_position_mapping()] {error_message}")
            return [error_message]
        if not (OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__FROSH_WEEK_CHAIR in position):
            error_message = "No valid indicator of whether position is for the Frosh Week Chair " \
                            "detected for position mapping"
            logger.info(f"[about/update_saved_position_mappings.py _update_position_mapping()] {error_message}")
            return [error_message]
        if not (OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__DISCORD_MANAGER in position):
            error_message = "No valid indicator of whether position is for the Discord Manager " \
                            "detected for position mapping"
            logger.info(f"[about/update_saved_position_mappings.py _update_position_mapping()] {error_message}")
            return [error_message]
        if not (OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__NUMBER_OF_TERMS in position):
            error_message = "No valid number of terms detected for position mapping"
            logger.info(f"[about/update_saved_position_mappings.py _update_position_mapping()] {error_message}")
            return [error_message]
        if not (OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__STARTING_MONTH in position):
            error_message = "No valid starting month detected for position mapping"
            logger.info(f"[about/update_saved_position_mappings.py _update_position_mapping()] {error_message}")
            return [error_message]

        position_mapping_for_selected_officer = OfficerEmailListAndPositionMapping.objects.get(
            id=int(position[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ID])
        )
        logger.info(
            f"[about/update_saved_position_mappings.py _update_position_mapping()] "
            f"user has selected to update the position {position_mapping_for_selected_officer.position_name}"
        )

        new_position_index_for_officer_position = int(
            position[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_INDEX]
        )
        new_name_for_officer_position = position[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_NAME]
        new_sfu_email_list_address_for_officer_position = \
            position[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__EMAIL_LIST_ADDRESS]
        discord_role_name = position[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__DISCORD_ROLE_NAME]
        github_access = position[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__GITHUB_ACCESS]
        google_drive_access = position[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__GOOGLE_DRIVE_ACCESS]
        elected_via_election_officer = \
            position[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ELECTED_VIA_ELECTION_OFFICER]
        executive_officer = position[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__EXECUTIVE_OFFICER]
        election_officer = position[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ELECTION_OFFICER]
        sfss_council_rep = position[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__SFSS_COUNCIL_REP]
        frosh_week_chair = position[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__FROSH_WEEK_CHAIR]
        discord_manager = position[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__DISCORD_MANAGER]
        number_of_terms = \
            position[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__NUMBER_OF_TERMS]
        starting_month = \
            position[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__STARTING_MONTH]

        if officer_info_is_not_changed(position_mapping_for_selected_officer,
                                       new_position_index_for_officer_position,
                                       new_name_for_officer_position,
                                       new_sfu_email_list_address_for_officer_position,
                                       discord_role_name,
                                       github_access,
                                       google_drive_access,
                                       elected_via_election_officer,
                                       executive_officer,
                                       election_officer,
                                       sfss_council_rep,
                                       frosh_week_chair,
                                       discord_manager,
                                       number_of_terms,
                                       starting_month,
                                       ):
            continue
        logger.info(
            f"[about/update_saved_position_mappings.py _update_position_mapping()] the user's "
            f"change to the position {position_mapping_for_selected_officer.position_name} was detected"
        )
        # if anything has been changed for the selected position
        success = True
        error_message = None
        previous_position_index = position_mapping_for_selected_officer.position_index
        previous_position_name = position_mapping_for_selected_officer.position_name
        if new_position_index_for_officer_position != previous_position_index:
            if new_position_index_for_officer_position in current_specified_position_indices:
                error_message = f"more than one position have been assigned an index of " \
                                f"{new_position_index_for_officer_position}"
                success = False
            else:
                current_specified_position_indices.append(new_position_index_for_officer_position)
        if success and new_name_for_officer_position != previous_position_name:
            if new_name_for_officer_position in current_specified_position_names:
                f"more than one position have been set to the name of {new_name_for_officer_position}"
                success = False
            else:
                current_specified_position_names.append(new_name_for_officer_position)

        if success:
            update_current_officer(positions_to_save, position_mapping_for_selected_officer,
                                   new_position_index_for_officer_position,
                                   new_sfu_email_list_address_for_officer_position, new_name_for_officer_position)
            update_elections_in_current_term(nominees_to_save, position_mapping_for_selected_officer,
                                             new_position_index_for_officer_position,
                                             new_name_for_officer_position
                                             )
            position_mapping_for_selected_officer.position_index = new_position_index_for_officer_position
            position_mapping_for_selected_officer.position_name = new_name_for_officer_position
            position_mapping_for_selected_officer.email = new_sfu_email_list_address_for_officer_position
            position_mapping_for_selected_officer.discord_role_name = discord_role_name
            position_mapping_for_selected_officer.github = github_access
            position_mapping_for_selected_officer.google_drive = google_drive_access
            position_mapping_for_selected_officer.elected_via_election_officer = elected_via_election_officer
            position_mapping_for_selected_officer.executive_officer = executive_officer
            position_mapping_for_selected_officer.election_officer = election_officer
            position_mapping_for_selected_officer.sfss_council_rep = sfss_council_rep
            position_mapping_for_selected_officer.frosh_week_chair = frosh_week_chair
            position_mapping_for_selected_officer.discord_manager = discord_manager
            position_mapping_for_selected_officer.number_of_terms = \
                OfficerEmailListAndPositionMapping.number_of_terms_choices_dict(front_end=False)[number_of_terms]
            position_mapping_for_selected_officer.starting_month = \
                OfficerEmailListAndPositionMapping.starting_month_choices_dict(front_end=False)[starting_month]
            position_mapping_for_selected_officer.save()
        else:
            logger.info(
                "[about/update_saved_position_mappings.py _update_position_mapping()]"
                f" encountered error {error_message} when trying to update position"
                f" {position_mapping_for_selected_officer.position_name}"
            )
        if error_message is not None:
            return [error_message]
    [position_to_save.save() for position_to_save in positions_to_save]
    [nominee_to_save.save() for nominee_to_save in nominees_to_save]
    return []


def officer_info_is_not_changed(position_mapping_for_selected_officer, new_position_index_for_officer_position,
                                new_name_for_officer_position,
                                new_sfu_email_list_address_for_officer_position,
                                discord_role_name,
                                github_access,
                                google_drive_access,
                                elected_via_election_officer,
                                executive_officer,
                                election_officer,
                                sfss_council_rep,
                                frosh_week_chair,
                                discord_manager,
                                number_of_terms, starting_month
                                ):
    """
    Returns a bool that indicates if the officer's info has been changed

    Keyword Arguments
    position_mapping_for_selected_officer -- the position mapping object for the officer position that may need
     to be updated
    new_name_for_officer_position -- the new name for the position mapping that may need to be updated
    new_position_index_for_officer_position -- the new index for the position mapping that may need to be updated
    new_sfu_email_list_address_for_officer_position -- the new sfu email list address for the position mapping
     that may need to be updated
    elected_via_election_officer -- the new status of whether a position is elected via election officer for
     the position mapping that may need to be updated
    number_of_terms -- the number of terms that a person generally has the position for
    starting_month -- the month when a new person is generally elected to the position

     Return
     bool -- true if a position_mapping_for_selected_officer has to be updated
    """
    return new_position_index_for_officer_position == position_mapping_for_selected_officer.position_index \
        and new_name_for_officer_position == position_mapping_for_selected_officer.position_name \
        and new_sfu_email_list_address_for_officer_position == position_mapping_for_selected_officer.email \
        and discord_role_name == position_mapping_for_selected_officer.discord_role_name \
        and github_access == position_mapping_for_selected_officer.github \
        and google_drive_access == position_mapping_for_selected_officer.google_drive \
        and elected_via_election_officer == position_mapping_for_selected_officer.elected_via_election_officer \
        and executive_officer == position_mapping_for_selected_officer.executive_officer \
        and election_officer == position_mapping_for_selected_officer.election_officer \
        and sfss_council_rep == position_mapping_for_selected_officer.sfss_council_rep \
        and frosh_week_chair == position_mapping_for_selected_officer.frosh_week_chair \
        and discord_manager == position_mapping_for_selected_officer.discord_manager \
        and number_of_terms == position_mapping_for_selected_officer.number_of_terms \
        and starting_month == position_mapping_for_selected_officer.starting_month


def update_current_officer(positions_to_save, position_mapping_for_selected_officer,
                           new_position_index_for_officer_position,
                           new_sfu_email_list_address_for_officer_position, new_name_for_officer_position):
    """
    updating the officer object under the current term with the new position mapping info

    Keyword Argument
    positions_to_save -- the list that has to contain all the officer objects that have to be added to for changes
     to be saved to DB
    position_mapping_for_selected_officer -- the position mapping object for the position that has to be updated
    new_name_for_officer_position -- the new name for the officer position that need to be updated
    new_position_index_for_officer_position -- the new index for the officer position that need to be updated
    new_sfu_email_list_address_for_officer_position -- the new sfu email list address for the officer position
     that need to be updated
    """
    terms = Term.objects.all().filter(term_number=get_current_term())
    if len(terms) == 1:
        term = terms[0]
        officers_in_current_term_that_need_update = Officer.objects.all().filter(
            elected_term=term,
            position_index=position_mapping_for_selected_officer.position_index
        )
        logger.info(
            f"[about/update_saved_position_mappings.py _update_position_mapping()] updating"
            f" {len(officers_in_current_term_that_need_update)} officers due to change in position"
            f" {position_mapping_for_selected_officer.position_name}"
        )
        for officer_in_current_term_that_need_update in officers_in_current_term_that_need_update:
            officer_in_current_term_that_need_update.position_index = new_position_index_for_officer_position
            officer_in_current_term_that_need_update.sfu_officer_mailing_list_email = \
                new_sfu_email_list_address_for_officer_position
            officer_in_current_term_that_need_update.position_name = new_name_for_officer_position
            positions_to_save.append(officer_in_current_term_that_need_update)


def update_elections_in_current_term(nominees_to_save, position_mapping_for_selected_officer,
                                     new_position_index_for_officer_position,
                                     new_name_for_officer_position):
    """
    Updating the nominee objects for nominees that have run for a position that needs to be updated
     in the current term

    Keyword Argument
    nominees_to_save -- the list that has to contain all the officer objects that have to be added to for changes
     to be saved to DB
    position_mapping_for_selected_officer -- the position mapping object for the position that has to be updated
    new_name_for_officer_position -- the new name for the nominee positions that need to be updated
    new_position_index_for_officer_position -- the new index for the nominee positions that need to be updated
    """
    nominees_to_update = NomineePosition.objects.all().filter(
        position_index=position_mapping_for_selected_officer.position_index,
        nominee_speech__nominee__election__date__gte=get_datetime_for_beginning_of_current_term()
    )
    for nominee_to_update in nominees_to_update:
        nominee_to_update.position_name = new_name_for_officer_position
        nominee_to_update.position_index = new_position_index_for_officer_position
        nominees_to_save.append(nominee_to_update)
