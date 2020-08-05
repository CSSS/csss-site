import datetime
import json
import logging

from django.http import HttpResponseRedirect
from django.shortcuts import render
from querystring_parser import parser
from django.conf import settings

from elections.models import NominationPage, Nominee
from csss.views_helper import verify_access_logged_user_and_create_context, \
    there_are_multiple_entries, ERROR_MESSAGE_KEY, create_main_context

NOM_NAME_POST_KEY = NOM_NAME_KEY = 'name'
NOM_POSITION_POST_KEY = NOM_POSITION_KEY = 'officer_position'
NOM_SPEECH_POST_KEY = NOM_SPEECH_KEY = 'speech'
NOM_FACEBOOK_POST_KEY = NOM_FACEBOOK_KEY = 'facebook'
NOM_LINKEDIN_POST_KEY = NOM_LINKEDIN_KEY = 'linked_in'
NOM_EMAIL_POST_KEY = NOM_EMAIL_KEY = 'email'
NOM_DISCORD_USERNAME_POST_KEY = NOM_DISCORD_USERNAME_KEY = 'discord'

ELECTION_TYPE_POST_KEY = ELECTION_TYPE_KEY = "election_type"
ELECTION_DATE_POST_KEY = ELECTION_DATE_KEY = "date"
ELECTION_WEBSURVEY_LINK_POST_KEY = ELECTION_WEBSURVEY_LINK_KEY = 'websurvey'
ELECTION_NOMINEES_POST_KEY = ELECTION_NOMINEES_KEY = 'nominees'
ELECTION_ID_SESSION_KEY = ELECTION_ID_POST_KEY = 'election_id'
ELECTION_TIME_POST_KEY = 'time'

DELETE_ACTION_POST_KEY = 'delete'
UPDATE_JSON_POST_KEY = 'json'
UPDATE_WEBFORM_POST_KEY = 'webform'
ELECTION_MODIFY_POST_KEY = 'modify'

ELECTION_DICT_POST_KEY = 'election_dict'

JSON_INPUT_FIELD_POST_KEY = 'input_json'

TAB_STRING = 'elections'

from elections.views.election_management_helper import _create_new_election_from_webform, \
    _save_nominees_for_new_election_from_webform, _validate_and_return_new_nominee, \
    _validate_and_return_information_for_new_election_from_json, _validate_new_nominees_for_new_election_from_json, \
    _get_information_for_election_user_wants_to_modify, _get_existing_election_by_id, \
    _validate_information_for_existing_election_from_webform_and_return_it, \
    _validate_nominees_information_for_existing_election_from_webform_and_return_them, \
    _update_nominee_information_for_existing_election_from_webform, \
    _update_information_for_existing_election_from_json, \
    _validate_nominee_information_for_existing_elections_from_json_and_save_all_changes # noqa

logger = logging.getLogger('csss_site')


def get_nominees(request, slug):
    context = create_main_context(request, TAB_STRING)
    retrieved_obj = NominationPage.objects.get(slug=slug)
    if retrieved_obj.date <= datetime.datetime.now():
        logger.info("[elections/election_management.py get_nominees()] time to vote")
        nominees = Nominee.objects.filter(nomination_page__slug=slug).all().order_by('position')
        context.update({
            'election': retrieved_obj,
            'election_date': retrieved_obj.date.strftime("%Y-%m-%d"),
            'nominees': nominees,
        })
        return render(request, 'elections/nominee_list.html', context)
    else:
        logger.info("[elections/election_management.py get_nominees()] cant vote yet")
        context.update({'nominees': 'none', })
        return render(request, 'elections/nominee_list.html', context)


# functions for showing user the pages for creating a new election
def show_page_for_user_to_enter_new_election_information_from_webform(request):
    """Shows the WebForm page where the user inputs the data needed to create new election"""
    logger.info(f"[elections/election_management.py "
                f"show_page_for_user_to_enter_new_election_information_from_webform()] request.POST={request.POST}")
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    return render(request, 'elections/create_election_webform.html', context)


def show_page_for_user_to_enter_new_election_information_from_json(request):
    """Shows the page where the json is displayed so that the user inputs the data needed to create a new election"""
    logger.info(
        "[elections/election_management.py show_page_for_user_to_enter_new_election_information_from_json()] "
        f"request.POST={request.POST}"
    )
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value

    if ERROR_MESSAGE_KEY in request.session:
        context[ERROR_MESSAGE_KEY] = request.session[ERROR_MESSAGE_KEY]
        context[JSON_INPUT_FIELD_POST_KEY] = json.dumps(request.session[JSON_INPUT_FIELD_POST_KEY])
        del request.session[ERROR_MESSAGE_KEY]
        del request.session[JSON_INPUT_FIELD_POST_KEY]
    else:
        nominee = {NOM_NAME_KEY: "", NOM_POSITION_KEY: "", NOM_SPEECH_KEY: "NONE", NOM_FACEBOOK_KEY: "NONE",
                   NOM_LINKEDIN_KEY: "NONE", NOM_EMAIL_KEY: "NONE", NOM_DISCORD_USERNAME_KEY: "NONE"}

        input_json_context = {ELECTION_TYPE_KEY: "", ELECTION_DATE_KEY: "YYYY-MM-DD HH:MM",
                              ELECTION_WEBSURVEY_LINK_KEY: "",
                              ELECTION_NOMINEES_KEY: [nominee]}

        context[JSON_INPUT_FIELD_POST_KEY] = json.dumps(input_json_context)
    return render(request, 'elections/create_election_json.html', context)


# functions for processing new election information DONE
def process_new_election_information_from_webform(request):
    """Processes the user's input from the WebForm page for creating a new election"""
    logger.info(f"[elections/election_management.py process_new_election_information_from_webform()] "
                f"request.POST={request.POST}")
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    updated_elections_information = parser.parse(request.POST.urlencode())
    if ELECTION_TYPE_POST_KEY in updated_elections_information and \
            ELECTION_DATE_POST_KEY in updated_elections_information and \
            ELECTION_TIME_POST_KEY in updated_elections_information and \
            ELECTION_WEBSURVEY_LINK_POST_KEY in updated_elections_information and \
            NOM_NAME_POST_KEY in updated_elections_information and \
            NOM_POSITION_POST_KEY in updated_elections_information and \
            NOM_SPEECH_POST_KEY in updated_elections_information and \
            NOM_FACEBOOK_POST_KEY in updated_elections_information and \
            NOM_LINKEDIN_POST_KEY in updated_elections_information and \
            NOM_EMAIL_POST_KEY in updated_elections_information and \
            NOM_DISCORD_USERNAME_POST_KEY in updated_elections_information:
        logger.info(f"[elections/election_management.py "
                    f"process_new_election_information_from_webform()] "
                    f"updated_elections_information={updated_elections_information}")
        election = _create_new_election_from_webform(updated_elections_information)
        if there_are_multiple_entries(updated_elections_information, NOM_NAME_POST_KEY):
            _save_nominees_for_new_election_from_webform(election, updated_elections_information)
        else:
            success, nominee, error_message = _validate_and_return_new_nominee(
                updated_elections_information[NOM_NAME_POST_KEY],
                updated_elections_information[NOM_POSITION_POST_KEY],
                updated_elections_information[NOM_SPEECH_POST_KEY],
                updated_elections_information[NOM_FACEBOOK_POST_KEY],
                updated_elections_information[NOM_LINKEDIN_POST_KEY],
                updated_elections_information[NOM_EMAIL_POST_KEY],
                updated_elections_information[NOM_DISCORD_USERNAME_POST_KEY], 0
            )
            if success and nominee is not None:
                nominee.nomination_page = election
                nominee.save()
                logger.info(
                    "[elections/election_management.py save_new_nominee()] saved user "
                    f"full_name={nominee.name} officer_position={nominee.officer_position}"
                    f" facebook_link={nominee.facebook} linkedin_link={nominee.linked_in} "
                    f"email_address={nominee.email} discord_username={nominee.discord}"
                )
        return HttpResponseRedirect(f'{settings.URL_ROOT}elections/{election.slug}/')
    else:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format("Not all necessary fields were detected in your input")
        return render_value


def process_new_election_information_from_json(request):
    """Processes the user's input from the JSON page for creating a new election"""
    logger.info("[elections/election_management.py process_new_election_information_from_json()] request.POST={"
                "request.POST}")
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    if JSON_INPUT_FIELD_POST_KEY in request.POST:
        logger.info("[elections/election_management.py process_new_election_information_from_json()] creating new "
                    "election")
        try:
            updated_elections_information = json.loads(request.POST[JSON_INPUT_FIELD_POST_KEY])
        except json.decoder.JSONDecodeError as e:
            logger.info(
                "[elections/election_management.py process_new_election_information_from_json()] "
                "experienced an error trying to interpet the json input from the user"
            )
            request.session[ERROR_MESSAGE_KEY] = f"Unable to decode the JSON input: {e}"
            request.session[JSON_INPUT_FIELD_POST_KEY] = json.dumps(
                request.POST[JSON_INPUT_FIELD_POST_KEY]
            ).replace("\\r", "").replace("\\n", "").replace("\\t", "").replace("\\", "")
            return HttpResponseRedirect(f"{settings.URL_ROOT}elections/show_create_json/")
        logger.info(
            "[elections/election_management.py process_new_election_information_from_json()] "
            f"updated_elections_information={updated_elections_information}")
        if ELECTION_TYPE_POST_KEY in updated_elections_information and \
                ELECTION_DATE_POST_KEY in updated_elections_information and \
                ELECTION_WEBSURVEY_LINK_POST_KEY in updated_elections_information and \
                ELECTION_NOMINEES_POST_KEY in updated_elections_information:
            success, nomination_page, error_message = _validate_and_return_information_for_new_election_from_json(
                updated_elections_information)
            if not success:
                request.session[ERROR_MESSAGE_KEY] = error_message
                request.session[JSON_INPUT_FIELD_POST_KEY] = updated_elections_information
                return HttpResponseRedirect(f"{settings.URL_ROOT}elections/show_create_json/")
            nominees = updated_elections_information[ELECTION_NOMINEES_POST_KEY]
            success, nominees, error_message = _validate_new_nominees_for_new_election_from_json(nominees)
            if not success:
                request.session[ERROR_MESSAGE_KEY] = error_message
                request.session[JSON_INPUT_FIELD_POST_KEY] = updated_elections_information
                return HttpResponseRedirect(f"{settings.URL_ROOT}elections/show_create_json/")
            nomination_page.save()
            logger.info(
                "[elections/election_management.py process_new_election_information_from_json()] nomination_page "
                f"{nomination_page} created with slug {nomination_page.slug}, "
                f"election_type={nomination_page.election_type}, date={nomination_page.date}, "
                f"websurvey={nomination_page.websurvey}, human_friendly_name={nomination_page.human_friendly_name} "
            )
            for nominee in nominees:
                nominee.nomination_page = nomination_page
                nominee.save()
                logger.info(
                    "[elections/election_management.py save_new_nominee()] saved user "
                    f"full_name={nominee.name} officer_position={nominee.officer_position}"
                    f" facebook_link={nominee.facebook} linkedin_link={nominee.linked_in} "
                    f"email_address={nominee.email} discord_username={nominee.discord}"
                )
            return HttpResponseRedirect(f'{settings.URL_ROOT}elections/{nomination_page.slug}/')
    request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format("Not all necessary fields were detected in your input")
    return render_value


# functions for allowing the user to select what action they want to take on an existing election
def show_page_where_user_can_select_election_to_update(request):
    """Shows the page where the user can choose an election and whether they want to update it via JSON or WebForm"""
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    elections = NominationPage.objects.all().order_by('-date')
    if len(elections) == 0:
        elections = None
    context.update({'elections': elections})
    return render(request, 'elections/list_elections_to_modify.html', context)


def determine_election_action(request):
    """Redirects the user to the page where they can edit the chosen election either via JSON or WebForm"""
    logger.info(f"[administration/election_management.py determine_election_action()] request.POST={request.POST}")
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    if ELECTION_MODIFY_POST_KEY in request.POST:
        if request.POST[ELECTION_MODIFY_POST_KEY] == UPDATE_JSON_POST_KEY and ELECTION_ID_POST_KEY in request.POST:
            request.session[ELECTION_ID_SESSION_KEY] = request.POST[ELECTION_ID_POST_KEY]
            return HttpResponseRedirect(f"{settings.URL_ROOT}elections/show_update_json")
        elif request.POST[ELECTION_MODIFY_POST_KEY] == UPDATE_WEBFORM_POST_KEY and \
                ELECTION_ID_POST_KEY in request.POST:
            request.session[ELECTION_ID_SESSION_KEY] = request.POST[ELECTION_ID_POST_KEY]
            return HttpResponseRedirect(f"{settings.URL_ROOT}elections/show_update_webform")
        elif request.POST[ELECTION_MODIFY_POST_KEY] == DELETE_ACTION_POST_KEY \
                and ELECTION_ID_POST_KEY in request.POST:
            request.session[ELECTION_ID_SESSION_KEY] = request.POST[ELECTION_ID_POST_KEY]
            return HttpResponseRedirect(f"{settings.URL_ROOT}elections/delete")
    logger.info(
        "[administration/election_management.py determine_election_action()] action "
        "is not detected, returning /elections/select_election"
    )
    return HttpResponseRedirect(f"{settings.URL_ROOT}elections/select_election")


# functions that display existing elections to students so they can update the chosen election
def show_page_for_user_to_modify_election_information_from_webform(request):
    """Shows the request election to the user in WebForm format"""
    logger.info(f"[administration/election_management.py "
                f"show_page_for_user_to_modify_election_information_from_webform()] request.POST={request.POST}")
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    if ELECTION_ID_SESSION_KEY in request.session:
        election_id = request.session[ELECTION_ID_SESSION_KEY]
        election = NominationPage.objects.get(id=election_id)
        nominees = [nominee for nominee in Nominee.objects.all().filter(nomination_page=election)]
        nominees.sort(key=lambda x: x.position, reverse=True)
        context.update({
            'election_id': election.id,
            'nominees': nominees,
            'election': election,
            'date': election.date.strftime("%Y-%m-%d"),
            'time': election.date.strftime("%H:%M"),
            'election_type': election.election_type,
            'websurvey': election.websurvey,
        })
        del request.session[ELECTION_ID_SESSION_KEY]
        return render(request, 'elections/update_election_webform.html', context)
    else:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format("Not all necessary fields were detected in your input")
        return render_value


def show_page_for_user_to_modify_election_information_from_json(request):
    """Shows the requested election to the user in JSON format"""
    logger.info(
        f"[administration/election_management.py show_page_for_user_to_modify_election_information_from_json()] "
        f"request.POST={request.POST}")
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    if ERROR_MESSAGE_KEY in request.session:
        context[ERROR_MESSAGE_KEY] = request.session[ERROR_MESSAGE_KEY]
        context[ELECTION_DICT_POST_KEY] = json.dumps(request.session[JSON_INPUT_FIELD_POST_KEY])
        context[ELECTION_ID_POST_KEY] = request.session[ELECTION_ID_SESSION_KEY]
        del request.session[ERROR_MESSAGE_KEY]
        del request.session[JSON_INPUT_FIELD_POST_KEY]
        del request.session[ELECTION_ID_SESSION_KEY]
        return render(request, 'elections/update_election_json.html', context)
    if ELECTION_ID_SESSION_KEY in request.session:
        election_id = request.session[ELECTION_ID_SESSION_KEY]
        election_dict = _get_information_for_election_user_wants_to_modify(
            election_id)
        context[ELECTION_DICT_POST_KEY] = json.dumps(election_dict)
        context[ELECTION_ID_POST_KEY] = election_id
        del request.session[ELECTION_ID_SESSION_KEY]
        return render(request, 'elections/update_election_json.html', context)
    else:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format("Not all necessary fields were detected in your input")
        return render_value


# functions for processing new information for existing elections
def process_existing_election_information_from_webform(request):
    """Updates the specified election using the WebForm input"""
    logger.info(
        "[elections/election_management.py process_existing_election_information_from_webform()] "
        f"request.POST={request.POST}"
    )
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    updated_elections_information = parser.parse(request.POST.urlencode())
    if ELECTION_TYPE_POST_KEY in updated_elections_information and \
            ELECTION_DATE_POST_KEY in updated_elections_information and \
            ELECTION_TIME_POST_KEY in updated_elections_information and \
            ELECTION_WEBSURVEY_LINK_POST_KEY in updated_elections_information and \
            ELECTION_ID_POST_KEY in updated_elections_information and \
            NOM_NAME_POST_KEY in updated_elections_information and \
            NOM_POSITION_POST_KEY in updated_elections_information and \
            NOM_SPEECH_POST_KEY in updated_elections_information and \
            NOM_FACEBOOK_POST_KEY in updated_elections_information and \
            NOM_LINKEDIN_POST_KEY in updated_elections_information and \
            NOM_EMAIL_POST_KEY in updated_elections_information and \
            NOM_DISCORD_USERNAME_POST_KEY in updated_elections_information:
        logger.info(
            "[elections/election_management.py process_existing_election_information_from_webform()] "
            "creating new election"
        )
        logger.info(
            "[elections/election_management.py process_existing_election_information_from_webform()] "
            f"updated_elections_information={updated_elections_information}")
        nomination_page = _get_existing_election_by_id(updated_elections_information[ELECTION_ID_POST_KEY])
        if nomination_page is None:
            request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(
                f"The Selected election for date {updated_elections_information[ELECTION_DATE_POST_KEY]} "
                "does not exist"
            )
            return render_value
        nom_page = _validate_information_for_existing_election_from_webform_and_return_it(
            nomination_page,
            updated_elections_information)
        if there_are_multiple_entries(updated_elections_information, NOM_NAME_POST_KEY):
            _validate_nominees_information_for_existing_election_from_webform_and_return_them(
                nom_page,
                updated_elections_information)
        else:
            _update_nominee_information_for_existing_election_from_webform(nomination_page,
                                                                           updated_elections_information)
        nom_page.save()
        return HttpResponseRedirect(f"{settings.URL_ROOT}elections/{nom_page.slug}")
    return HttpResponseRedirect(f"{settings.URL_ROOT}elections/select_election_to_update")


def process_existing_election_information_from_json(request):
    """Updates the specified election using the JSON input"""
    logger.info(
        "[elections/election_management.py process_existing_election_information_from_json()] "
        f"request.POST={request.POST}"
    )
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    if JSON_INPUT_FIELD_POST_KEY in request.POST and ELECTION_ID_POST_KEY in request.POST:
        logger.info(
            "[elections/election_management.py process_existing_election_information_from_json()] "
            "creating new election"
        )
        election_id = request.POST[ELECTION_ID_POST_KEY]
        try:
            updated_elections_information = json.loads(request.POST[JSON_INPUT_FIELD_POST_KEY])
        except json.decoder.JSONDecodeError as e:
            logger.info(
                "[elections/election_management.py process_existing_election_information_from_json()] "
                "experienced an error trying to interpet the json input from the user"
            )
            request.session[ERROR_MESSAGE_KEY] = f"Unable to decode the JSON input: {e}"
            request.session[JSON_INPUT_FIELD_POST_KEY] = json.dumps(
                request.POST[JSON_INPUT_FIELD_POST_KEY]
            ).replace("\\r", "").replace("\\n", "").replace("\\t", "").replace("\\", "")
            request.session[ELECTION_ID_SESSION_KEY] = election_id
            return HttpResponseRedirect(f"{settings.URL_ROOT}elections/show_update_json")
        nomination_page = _get_existing_election_by_id(election_id)
        if nomination_page is None:
            request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(
                f"The Selected election for date {updated_elections_information[ELECTION_DATE_POST_KEY]} "
                "does not exist"
            )
            request.session[JSON_INPUT_FIELD_POST_KEY] = updated_elections_information
            request.session[ELECTION_ID_SESSION_KEY] = election_id
            return HttpResponseRedirect(f"{settings.URL_ROOT}elections/show_update_json")
        logger.info(
            f"[elections/election_management.py process_existing_election_information_from_json()] "
            f"updated_elections_information={updated_elections_information}")
        if ELECTION_DATE_POST_KEY in updated_elections_information and \
                ELECTION_TYPE_POST_KEY in updated_elections_information and \
                ELECTION_WEBSURVEY_LINK_POST_KEY in updated_elections_information and \
                ELECTION_NOMINEES_POST_KEY in updated_elections_information:
            success, nomination_page, error_message = _update_information_for_existing_election_from_json(
                nomination_page, updated_elections_information)
            if not success:
                request.session[ERROR_MESSAGE_KEY] = error_message
                request.session[JSON_INPUT_FIELD_POST_KEY] = updated_elections_information
                request.session[ELECTION_ID_SESSION_KEY] = election_id
                return HttpResponseRedirect(f"{settings.URL_ROOT}elections/show_update_json")
            success, error_message = \
                _validate_nominee_information_for_existing_elections_from_json_and_save_all_changes(
                    nomination_page, updated_elections_information[ELECTION_NOMINEES_POST_KEY])
            if not success:
                request.session[ERROR_MESSAGE_KEY] = error_message
                request.session[JSON_INPUT_FIELD_POST_KEY] = updated_elections_information
                request.session[ELECTION_ID_SESSION_KEY] = election_id
                return HttpResponseRedirect(f"{settings.URL_ROOT}elections/show_update_json")
            return HttpResponseRedirect(f'{settings.URL_ROOT}elections/{nomination_page.slug}/')
    request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format("Not all necessary fields were detected in your input")
    return render_value


def delete_selected_election(request):
    logger.info(f"[administration/election_management.py "
                f"delete_selected_election()] request.POST={request.POST}")
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    if ELECTION_ID_SESSION_KEY in request.session:
        election_id = request.session[ELECTION_ID_SESSION_KEY]
        del request.session[ELECTION_ID_SESSION_KEY]
        NominationPage.objects.get(id=election_id).delete()
        return HttpResponseRedirect(f'{settings.URL_ROOT}elections/select_election_to_update/')
    request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format("Could not detect the election ID in your request")
    return render_value


def list_of_elections(request):
    logger.info("[administration/election_management.py list_of_elections()]")
    context = create_main_context(request, TAB_STRING)
    return render(request, 'elections/list_elections.html', context)
