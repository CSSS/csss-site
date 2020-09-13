import logging

from django.shortcuts import render
from querystring_parser import parser

from about.models import OfficerEmailListAndPositionMapping, Term, Officer
from about.views.officer_management_helper import TAB_STRING
from csss.views_helper import verify_access_logged_user_and_create_context, ERROR_MESSAGE_KEY, \
    there_are_multiple_entries, get_current_active_term, ERROR_MESSAGES_KEY

logger = logging.getLogger('csss_site')

OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ID = "officer_email_list_and_position_mapping__id"
OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_INDEX = "officer_email_list_and_position_mapping__position_index"
OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_TYPE = "officer_email_list_and_position_mapping__position_name"
OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__EMAIL_LIST_ADDRESS = \
    "officer_email_list_and_position_mapping__email_list_address "


def position_mapping(request):
    """
    Handles any modifications done to position mappings
    """
    logger.info(
        f"[about/position_mapping.py position_mapping()] request.POST={request.POST}")
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request,
                                                                                          TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = f'{error_message}<br>'
        return render_value
    context['OFFICER_POSITION_MAPPING__ID_KEY'] = OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ID
    context['OFFICER_POSITION_MAPPING__POSITION_INDEX_KEY'] = OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_INDEX
    context['OFFICER_POSITION_MAPPING__POSITION_NAME_KEY'] = OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_TYPE
    context['OFFICER_POSITION_MAPPING__POSITION_EMAIL_KEY'] = \
        OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__EMAIL_LIST_ADDRESS

    if request.method == "POST":
        post_dict = parser.parse(request.POST.urlencode())
        if 'action' in post_dict:  # modifying an existing position mapping
            if post_dict['action'] == "update":
                position_mapping_for_selected_officer = OfficerEmailListAndPositionMapping.objects.get(
                    id=post_dict[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ID]
                )

                new_position_index_for_officer_position = int(
                    post_dict[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_INDEX]
                )
                new_name_for_officer_position = post_dict[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_TYPE]
                new_sfu_email_list_address_for_officer_position = post_dict[
                    OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__EMAIL_LIST_ADDRESS
                ]
                logger.info("[about/position_mapping.py position_mapping()] user has selected to update the "
                            f"position {position_mapping_for_selected_officer.officer_position} ")

                if not (new_name_for_officer_position == position_mapping_for_selected_officer.officer_position and
                        new_position_index_for_officer_position ==
                        position_mapping_for_selected_officer.term_position_number and
                        new_sfu_email_list_address_for_officer_position ==
                        position_mapping_for_selected_officer.email):
                    logger.info("[about/position_mapping.py position_mapping()] the user's change to the position "
                                f"{position_mapping_for_selected_officer.officer_position} was detected")
                    # if anything has been changed for the selected position
                    success = True
                    previpus_position_index = position_mapping_for_selected_officer.term_position_number
                    previous_position_name = position_mapping_for_selected_officer.officer_position
                    if new_position_index_for_officer_position != previpus_position_index:
                        success, error_message = validate_position_index(new_position_index_for_officer_position)
                    if success and new_name_for_officer_position != previous_position_name:
                        success, error_message = validate_position_name(new_name_for_officer_position)

                    if success:
                        terms = Term.objects.all().filter(term_number=get_current_active_term())
                        if len(terms) > 0:
                            term = terms[0]
                            officer_in_current_term_that_need_update = Officer.objects.all().filter(
                                elected_term=term,
                                position=position_mapping_for_selected_officer.officer_position
                            )
                            logger.info("[about/position_mapping.py position_mapping()] updating "
                                        f"{len(officer_in_current_term_that_need_update)} officers "
                                        f"due to change in position "
                                        f"{position_mapping_for_selected_officer.officer_position}")
                            for officer in officer_in_current_term_that_need_update:
                                officer.term_position_number = new_position_index_for_officer_position
                                officer.sfu_officer_mailing_list_email = \
                                    new_sfu_email_list_address_for_officer_position
                                officer.position = new_name_for_officer_position
                                officer.save()
                        position_mapping_for_selected_officer.officer_position = new_name_for_officer_position
                        position_mapping_for_selected_officer.term_position_number = \
                            new_position_index_for_officer_position
                        position_mapping_for_selected_officer.email = new_sfu_email_list_address_for_officer_position
                        position_mapping_for_selected_officer.save()
                    else:
                        logger.info("[about/position_mapping.py position_mapping()] encountered error "
                                    f"{error_message} when trying to update "
                                    f"position {position_mapping_for_selected_officer.officer_position}")
                        context[ERROR_MESSAGES_KEY] = [error_message]
            elif post_dict['action'] == "delete" or post_dict['action'] == "un_delete":
                position_mapping_for_selected_officer = OfficerEmailListAndPositionMapping.objects.get(
                    id=post_dict[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ID]
                )
                position_mapping_for_selected_officer.marked_for_deletion = post_dict['action'] == "delete"
                logger.info("[about/position_mapping.py position_mapping()] deletion for position "
                            f"{position_mapping_for_selected_officer.officer_position} set to  "
                            f"{position_mapping_for_selected_officer.marked_for_deletion}")
                position_mapping_for_selected_officer.save()
        else:  # adding new position mapping[s]
            if there_are_multiple_entries(post_dict, "position_name"):
                logger.info("[about/position_mapping.py position_mapping()] it appears that the"
                            " user wants to create multiple new officers")
                error_detected = False
                unsaved_position_mappings = []  # used to display all the submitted position if one of them had an
                # error which causes none of them to be saved

                # saves the position and position indexes checked so far so that the validator can check the
                # given position and its index against all in the database and the previous checked
                # positions and their indices
                submitted_positions = []
                submitted_position_indexes = []
                number_of_entries = len(post_dict["position_name"])
                context[ERROR_MESSAGES_KEY] = []
                for index in range(number_of_entries):
                    position_name = post_dict["position_name"][index]
                    position_index = post_dict["position_index"][index]
                    position_email = post_dict["position_email"][index]
                    unsaved_position_mappings.append(
                        {"position_name": position_name, "position_index": position_index,
                         "position_email": position_email}
                    )
                    success, error_message = validate_position_mappings(
                        position_index, position_name,
                        submitted_positions=submitted_positions, submitted_position_indexes=submitted_position_indexes
                    )
                    submitted_positions.append(position_name)
                    submitted_position_indexes.append(position_index)
                    if not success:
                        context[ERROR_MESSAGES_KEY].extend(f"{error_message}")
                        logger.info("[about/position_mapping.py position_mapping()] "
                                    "unable to validate the new position"
                                    f" {position_name} due to {error_message}")
                        error_detected = True
                if error_detected:
                    context["unsaved_position_mappings"] = unsaved_position_mappings
                else:
                    del context[ERROR_MESSAGES_KEY]
                    logger.info("[about/position_mapping.py position_mapping()] all new positions passed validation")
                    for index in range(number_of_entries):
                        OfficerEmailListAndPositionMapping(officer_position=post_dict["position_name"][index],
                                                           term_position_number=post_dict["position_index"][index],
                                                           email=post_dict["position_email"][index]).save()
            else:
                success, error_message = validate_position_mappings(post_dict["position_index"],
                                                                    post_dict["position_name"])
                if success:
                    logger.info("[about/position_mapping.py position_mapping()] new position"
                                f" {post_dict['position_name']} passed validation")

                    OfficerEmailListAndPositionMapping(officer_position=post_dict["position_name"],
                                                       term_position_number=post_dict["position_index"],
                                                       email=post_dict["position_email"]).save()
                else:
                    logger.info(f"[about/position_mapping.py position_mapping()] unable to save new position "
                                f"{post_dict['position_name']} due to error {error_message}")
                    unsaved_position_mappings = [
                        {"position_name": post_dict["position_name"], "position_index": post_dict["position_index"],
                         "position_email": post_dict["position_email"]}]
                    context["unsaved_position_mappings"] = unsaved_position_mappings
                    context[ERROR_MESSAGES_KEY] = [error_message]
    position_mapping_for_selected_officer = OfficerEmailListAndPositionMapping.objects.all().order_by(
        'term_position_number')
    if len(position_mapping_for_selected_officer) > 0:
        context['position_mapping'] = position_mapping_for_selected_officer
    return render(request, 'about/position_mapping.html', context)


def validate_position_index(position_index, submitted_position_indexes=None):
    """
    Validates the new inputted position index

    Keyword Argument
    position_index -- the new position index
    submitted_position_indexes -- other indexes specified by the user so far
     if they are submitting multiple positions at once

    Return
    success -- True or False if the new position index is not already used
    error_message -- an error_message if the index was already used
    """
    if submitted_position_indexes is None:
        submitted_position_indexes = []
    if len(OfficerEmailListAndPositionMapping.objects.all().filter(
            term_position_number=position_index)) > 0 or position_index in submitted_position_indexes:
        logger.info(f"[about/position_mapping.py validate_position_index()] validate for position index "
                    f"{position_index} was unsuccessful")
        return False, f"Another Position already has an index of {position_index}"
    logger.info(f"[about/position_mapping.py validate_position_index()] validate for position index "
                f"{position_index} was successful")
    return True, None


def validate_position_name(position_name, submitted_position_names=None):
    """
    Validates the new inputted position name

    Keyword Argument
    position_name -- the new position name
    submitted_position_names -- other names specified by the user so far if they
     are submitting multiple positions at once

    Return
    success -- True or False if the new position name is not already used
    error_message -- an error_message if the name was already used
    """
    if submitted_position_names is None:
        submitted_position_names = []
    if len(OfficerEmailListAndPositionMapping.objects.all().filter(
            officer_position=position_name)) > 0 or position_name in submitted_position_names:
        logger.info(f"[about/position_mapping.py validate_position_name()] validate for position name "
                    f"{position_name} was unsuccessful")
        return False, f"the position of {position_name} already exists"
    logger.info(f"[about/position_mapping.py validate_position_name()] validate for position name "
                f"{position_name} was successful")
    return True, None


def validate_position_mappings(position_index, position_name, submitted_positions=None,
                               submitted_position_indexes=None):
    """
    Validates the new inputted position name and index

    Keyword Argument
    position_name -- the new position name
    position_index -- the new position index
    submitted_position_names -- other names specified by the user so far if they are
     submitting multiple positions at once
    submitted_position_indexes -- other indexes specified by the user so far if they are submitting
     multiple positions at once

    Return
    success -- True or False if the new position name or index is not already used
    error_message -- an error_message if the name or index was already used
    """
    success, error_message = validate_position_index(position_index, submitted_position_indexes)
    if not success:
        return success, error_message
    success, error_message = validate_position_name(position_name, submitted_positions)
    if not success:
        return success, error_message
    return True, None
