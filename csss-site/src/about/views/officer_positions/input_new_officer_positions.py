from django.shortcuts import render
from querystring_parser import parser

from about.models import OfficerEmailListAndPositionMapping
from about.views.Constants import TAB_STRING
from about.views.position_mapping_helper import update_context, validate_position_index, validate_position_name, \
    POSITION_INDEX_KEY, validate_elected_via_election_officer_status, validate_number_of_terms, \
    validate_starting_month, validate_github_access, validate_google_drive_access, \
    validate_executive_officer_status, validate_election_officer_status, \
    validate_sfss_council_representative_status, validate_frosh_week_chair_status, \
    validate_discord_manager_status
from csss.setup_logger import Loggers
from csss.views.context_creation.create_authenticated_contexts import create_context_for_updating_position_mappings
from csss.views.views import ERROR_MESSAGES_KEY
from csss.views_helper import there_are_multiple_entries

POSITION_NAME_KEY = 'position_name'
POSITION_EMAIL_KEY = 'position_email'
ELECTED_VIA_ELECTION_OFFICER_KEY = 'elected_via_election_officer'
GITHUB_ACCESS__KEY = 'github'
GOOGLE_DRIVE_ACCESS__KEY = 'google_drive'
EXECUTIVE_OFFICER_KEY = 'executive_officer'
ELECTION_OFFICER_KEY = 'election_officer'
SFSS_COUNCIL_REPRESENTATIVE_KEY = 'sfss_council_rep'
FROSH_WEEK_CHAIR_KEY = 'frosh_week_chair'
DISCORD_MANAGER_KEY = 'discord_manager'
DISCORD_ROLE_NAME_KEY = 'discord_role_name'
NUMBER_OF_TERMS_KEY = 'number_of_terms'
STARTING_MONTH_KEY = 'starting_month'
UNSAVED_POSITION_MAPPINGS_KEY = 'unsaved_position_mappings'


def input_new_officer_positions(request):
    logger = Loggers.get_logger()
    logger.info("[about/input_new_officer_positions.py input_new_officer_positions()]"
                f" request.POST={request.POST}")
    context = create_context_for_updating_position_mappings(request, tab=TAB_STRING)
    context[ERROR_MESSAGES_KEY] = []
    if request.method == "POST":
        post_dict = parser.parse(request.POST.urlencode())
        if 'add_new_position_mapping' in post_dict:
            success, context[ERROR_MESSAGES_KEY], context[UNSAVED_POSITION_MAPPINGS_KEY] = \
                _add_new_position_mapping(post_dict)
    return render(request, 'about/officer_positions/officer_positions.html', update_context(context))


def _add_new_position_mapping(post_dict):
    """
    Adds a new officer position mapping

    Keyword Argument
    post_dict -- request.POST in dictionary object

    Return
    success -- bool that is True or false
    error_message -- an error_message if the specified position index and position name are already used
    unsaved_position_mappings -- a dict that contains the unsaved position index
     and position names if one of them was invalid
    """
    logger = Loggers.get_logger()
    error_messages = []
    starting_months = OfficerEmailListAndPositionMapping.starting_month_choices_dict(front_end=False)
    if there_are_multiple_entries(post_dict, POSITION_NAME_KEY):
        logger.info(
            "[about/input_new_officer_positions.py _add_new_position_mapping()] it appears "
            "that the user wants to create multiple new officers"
        )
        error_detected = False
        unsaved_position_mappings = []  # used to display all the submitted position if one of them had an
        # error which causes none of them to be saved

        # saves the position and position indexes checked so far so that the validator can check the
        # given position and its index against all in the database and the previous checked
        # positions and their indices
        submitted_position_names = []
        submitted_position_indices = []
        number_of_entries = len(post_dict[POSITION_NAME_KEY])
        for index in range(number_of_entries):
            position_name = post_dict[POSITION_NAME_KEY][index]
            position_index = post_dict[POSITION_INDEX_KEY][index]
            position_email = post_dict[POSITION_EMAIL_KEY][index]
            number_of_terms = int(post_dict[NUMBER_OF_TERMS_KEY][index]) \
                if f"{post_dict[NUMBER_OF_TERMS_KEY][index]}".isdigit() else None
            starting_month = starting_months[post_dict[STARTING_MONTH_KEY][index]] \
                if post_dict[STARTING_MONTH_KEY][index] in starting_months else None
            elected_via_election_officer = post_dict[ELECTED_VIA_ELECTION_OFFICER_KEY][index]
            github_access = post_dict[GITHUB_ACCESS__KEY][index]
            google_drive_access = post_dict[GOOGLE_DRIVE_ACCESS__KEY][index]
            executive_officer = post_dict[EXECUTIVE_OFFICER_KEY][index]
            election_officer = post_dict[ELECTION_OFFICER_KEY][index]
            sfss_council_representative = post_dict[SFSS_COUNCIL_REPRESENTATIVE_KEY][index]
            frosh_week_chair = post_dict[FROSH_WEEK_CHAIR_KEY][index]
            discord_manager = post_dict[DISCORD_MANAGER_KEY][index]
            discord_role_name = post_dict[DISCORD_ROLE_NAME_KEY][index]
            unsaved_position_mappings.append(
                {POSITION_INDEX_KEY: position_index, POSITION_NAME_KEY: position_name,
                 POSITION_EMAIL_KEY: position_email,
                 DISCORD_ROLE_NAME_KEY: discord_role_name,
                 GITHUB_ACCESS__KEY: github_access == 'True',
                 GOOGLE_DRIVE_ACCESS__KEY: google_drive_access == 'True',
                 ELECTED_VIA_ELECTION_OFFICER_KEY: elected_via_election_officer == 'True',
                 EXECUTIVE_OFFICER_KEY: executive_officer == 'True',
                 ELECTION_OFFICER_KEY: election_officer == 'True',
                 SFSS_COUNCIL_REPRESENTATIVE_KEY: sfss_council_representative == 'True',
                 FROSH_WEEK_CHAIR_KEY: frosh_week_chair == 'True',
                 DISCORD_MANAGER_KEY: discord_manager == 'True',
                 NUMBER_OF_TERMS_KEY: post_dict[NUMBER_OF_TERMS_KEY][index],
                 STARTING_MONTH_KEY: post_dict[STARTING_MONTH_KEY][index]
                 }
            )
            success, error_message = _validate_position_mappings(
                position_index, position_name, github_access, google_drive_access, elected_via_election_officer,
                executive_officer, election_officer, sfss_council_representative, frosh_week_chair, discord_manager,
                number_of_terms, starting_month,
                submitted_position_names=submitted_position_names,
                submitted_position_indices=submitted_position_indices
            )
            submitted_position_names.append(position_name)
            submitted_position_indices.append(position_index)
            if not success:
                error_messages.append(f"{error_message}")
                logger.info(
                    "[about/input_new_officer_positions.py _add_new_position_mapping()] "
                    f"unable to validate the new position {position_name} due to {error_message}"
                )
                error_detected = True
        if error_detected:
            return False, error_messages, unsaved_position_mappings
        else:
            logger.info(
                "[about/input_new_officer_positions.py _add_new_position_mapping()] "
                "all new positions passed validation"
            )
            for index in range(number_of_entries):
                OfficerEmailListAndPositionMapping(
                    position_index=post_dict[POSITION_INDEX_KEY][index],
                    position_name=post_dict[POSITION_NAME_KEY][index],
                    email=post_dict[POSITION_EMAIL_KEY][index],
                    discord_role_name=post_dict[DISCORD_ROLE_NAME_KEY][index],
                    github=post_dict[GITHUB_ACCESS__KEY][index] == 'True',
                    google_drive=post_dict[GOOGLE_DRIVE_ACCESS__KEY][index] == 'True',
                    elected_via_election_officer=post_dict[ELECTED_VIA_ELECTION_OFFICER_KEY][index] == 'True',
                    executive_officer=post_dict[EXECUTIVE_OFFICER_KEY][index] == 'True',
                    election_officer=post_dict[ELECTION_OFFICER_KEY][index] == 'True',
                    sfss_council_rep=post_dict[SFSS_COUNCIL_REPRESENTATIVE_KEY][index] == 'True',
                    frosh_week_chair=post_dict[FROSH_WEEK_CHAIR_KEY][index] == 'True',
                    discord_manager=post_dict[DISCORD_MANAGER_KEY][index] == 'True',
                    number_of_terms=int(post_dict[NUMBER_OF_TERMS_KEY][index])
                    if f"{post_dict[NUMBER_OF_TERMS_KEY][index]}".isdigit() else None,
                    starting_month=starting_months[post_dict[STARTING_MONTH_KEY][index]]
                    if post_dict[STARTING_MONTH_KEY][index] in starting_months else None
                ).save()
    else:
        success, error_message = \
            _validate_position_mappings(post_dict[POSITION_INDEX_KEY], post_dict[POSITION_NAME_KEY],
                                        post_dict[GITHUB_ACCESS__KEY],
                                        post_dict[GOOGLE_DRIVE_ACCESS__KEY],
                                        post_dict[ELECTED_VIA_ELECTION_OFFICER_KEY],
                                        post_dict[EXECUTIVE_OFFICER_KEY],
                                        post_dict[ELECTION_OFFICER_KEY],
                                        post_dict[SFSS_COUNCIL_REPRESENTATIVE_KEY],
                                        post_dict[FROSH_WEEK_CHAIR_KEY],
                                        post_dict[DISCORD_MANAGER_KEY],
                                        int(post_dict[NUMBER_OF_TERMS_KEY])
                                        if f"{post_dict[NUMBER_OF_TERMS_KEY]}".isdigit() else None,
                                        starting_months[post_dict[STARTING_MONTH_KEY]]
                                        if post_dict[STARTING_MONTH_KEY] in starting_months else None
                                        )
        if success:
            logger.info(
                f"[about/input_new_officer_positions.py _add_new_position_mapping()] "
                f"new position {post_dict[POSITION_NAME_KEY]} passed validation"
            )

            OfficerEmailListAndPositionMapping(
                position_index=post_dict[POSITION_INDEX_KEY],
                position_name=post_dict[POSITION_NAME_KEY],
                email=post_dict[POSITION_EMAIL_KEY],
                discord_role_name=post_dict[DISCORD_ROLE_NAME_KEY],
                github=post_dict[GITHUB_ACCESS__KEY] == 'True',
                google_drive=post_dict[GOOGLE_DRIVE_ACCESS__KEY] == 'True',
                elected_via_election_officer=post_dict[ELECTED_VIA_ELECTION_OFFICER_KEY] == 'True',
                executive_officer=post_dict[EXECUTIVE_OFFICER_KEY] == 'True',
                election_officer=post_dict[ELECTION_OFFICER_KEY] == 'True',
                sfss_council_rep=post_dict[SFSS_COUNCIL_REPRESENTATIVE_KEY] == 'True',
                frosh_week_chair=post_dict[FROSH_WEEK_CHAIR_KEY] == 'True',
                discord_manager=post_dict[DISCORD_MANAGER_KEY] == 'True',
                number_of_terms=int(post_dict[NUMBER_OF_TERMS_KEY])
                if f"{post_dict[NUMBER_OF_TERMS_KEY]}".isdigit() else None,
                starting_month=starting_months[post_dict[STARTING_MONTH_KEY]]
                if post_dict[STARTING_MONTH_KEY] in starting_months else None
            ).save()
        else:
            logger.info(
                f"[about/input_new_officer_positions.py _add_new_position_mapping()] unable to "
                f"save new position {post_dict[POSITION_NAME_KEY]} due to error {error_message}"
            )
            unsaved_position_mappings = [
                {POSITION_INDEX_KEY: post_dict[POSITION_INDEX_KEY], POSITION_NAME_KEY: post_dict[POSITION_NAME_KEY],
                 POSITION_EMAIL_KEY: post_dict[POSITION_EMAIL_KEY],
                 DISCORD_ROLE_NAME_KEY: post_dict[DISCORD_ROLE_NAME_KEY],
                 GITHUB_ACCESS__KEY: post_dict[GITHUB_ACCESS__KEY] == 'True',
                 GOOGLE_DRIVE_ACCESS__KEY: post_dict[GOOGLE_DRIVE_ACCESS__KEY] == 'True',
                 ELECTED_VIA_ELECTION_OFFICER_KEY: post_dict[ELECTED_VIA_ELECTION_OFFICER_KEY] == 'True',
                 EXECUTIVE_OFFICER_KEY: post_dict[EXECUTIVE_OFFICER_KEY] == 'True',
                 ELECTION_OFFICER_KEY: post_dict[ELECTION_OFFICER_KEY] == 'True',
                 SFSS_COUNCIL_REPRESENTATIVE_KEY: post_dict[SFSS_COUNCIL_REPRESENTATIVE_KEY] == 'True',
                 FROSH_WEEK_CHAIR_KEY: post_dict[FROSH_WEEK_CHAIR_KEY] == 'True',
                 DISCORD_MANAGER_KEY: post_dict[DISCORD_MANAGER_KEY] == 'True',
                 NUMBER_OF_TERMS_KEY: post_dict[NUMBER_OF_TERMS_KEY],
                 STARTING_MONTH_KEY: post_dict[STARTING_MONTH_KEY],
                 }
            ]
            error_messages.append(error_message)
            return False, error_messages, unsaved_position_mappings
    return True, error_messages, None


def _validate_position_mappings(position_index, position_name, github_access, google_drive_access,
                                elected_via_election_officer, executive_officer, election_officer,
                                sfss_council_representative, frosh_week_chair, discord_manager,
                                number_of_terms, starting_month,
                                submitted_position_names=None, submitted_position_indices=None):
    """
    Validates the new inputted position name and index

    Keyword Argument
    position_index -- the new position index
    position_name -- the new position name
    elected_via_election_officer -- indicator of whether the position's election is done by the election officer
    number_of_terms -- the number of terms that the position would normally last for
    starting_month -- the month when a new person normally starts in the position
    submitted_position_names -- other names specified by the user so far if they are
     submitting multiple positions at once
    submitted_position_indices -- other indexes specified by the user so far if they are submitting
     multiple positions at once

    Return
    success -- True or False if the new position name or index is not already used
    error_message -- an error_message if the name or index was already used
    """
    success, error_message = validate_position_index(position_index, submitted_position_indices)
    if not success:
        return success, error_message
    success, error_message = validate_position_name(position_name, submitted_position_names)
    if not success:
        return success, error_message
    success, error_message = validate_github_access(github_access)
    if not success:
        return success, error_message
    success, error_message = validate_google_drive_access(google_drive_access)
    if not success:
        return success, error_message
    success, error_message = validate_elected_via_election_officer_status(elected_via_election_officer)
    if not success:
        return success, error_message

    success, error_message = validate_executive_officer_status(executive_officer)
    if not success:
        return success, error_message
    success, error_message = validate_election_officer_status(election_officer)
    if not success:
        return success, error_message
    success, error_message = validate_sfss_council_representative_status(sfss_council_representative)
    if not success:
        return success, error_message
    success, error_message = validate_frosh_week_chair_status(frosh_week_chair)
    if not success:
        return success, error_message
    success, error_message = validate_discord_manager_status(discord_manager)
    if not success:
        return success, error_message
    success, error_message = validate_number_of_terms(number_of_terms)
    if not success:
        return success, error_message
    return validate_starting_month(starting_month)
