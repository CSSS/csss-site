import datetime
from django.http import HttpResponseRedirect
from django.shortcuts import render
from elections.models import NominationPage, Nominee
import json
import logging
from querystring_parser import parser
from django.conf import settings

logger = logging.getLogger('csss_site')

NOM_NAME_KEY = 'name'
NOM_POSITION_KEY = 'officer_position'
NOM_SPEECH_KEY = 'speech'
NOM_FACEBOOK_KEY = 'facebook'
NOM_LINKEDIN_KEY = 'linked_in'
NOM_EMAIL_KEY = 'email'
NOM_DISCORD_USERNAME_KEY = 'discord'

ELECTION_TYPE_KEY = 'election_type'
ELECTION_DATE_KEY = 'date'
ELECTION_WEBSURVEY_LINK_KEY = 'websurvey'
ELECTION_NOMINEES_KEY = 'nominees'
ELECTION_ID_KEY = 'election_id'

DELETE_ACTION_POST_KEY = 'delete'
UPDATE_ACTION_POST_KEY = 'update'
UPDATE_WITH_JSON_ACTION_POST_KEY = 'update_with_json'

ELECTION_DATE_POST_KEY = 'date'
ELECTION_TIME_POST_KEY = 'time'

JSON_INPUT_POST_KEY = 'input_json'


def create_specified_election(request):
    logger.info(f"[administration/views.py create_specified_election()] request.POST={request.POST}")
    groups = list(request.user.groups.values_list('name', flat=True))
    context = {
        'tab': 'administration',
        'authenticated': request.user.is_authenticated,
        'Officer': ('Officer' in groups),
        'ElectionOfficer': ('ElectionOfficer' in groups),
        'Staff': request.user.is_staff,
        'Username': request.user.username,
        'URL_ROOT': settings.URL_ROOT
    }
    if not ('ElectionOfficer' in groups or request.user.is_staff or 'Officer' in groups):
        return render(request, 'administration/invalid_access.html', context)
    if ELECTION_TYPE_KEY in request.POST and ELECTION_DATE_POST_KEY in request.POST and \
            ELECTION_TIME_POST_KEY in request.POST and ELECTION_WEBSURVEY_LINK_KEY in request.POST:
        logger.info("[administration/views.py create_specified_election()] creating new election")
        nomination_page = get_nomination_page(request.POST)
        post_dict = parser.parse(request.POST.urlencode())
        logger.info(f"[administration/views.py create_specified_election()] post_dict={post_dict}")
        logger.info(
            "[administration/views.py create_specified_election()] "
            f"full_name={post_dict[NOM_NAME_KEY]} len = {len(post_dict[NOM_NAME_KEY])}"
        )
        position_index = 0
        if (len(post_dict[NOM_NAME_KEY][0]) > 1):
            save_nominees(post_dict, nomination_page, position_index)
            position_index += 1
        else:
            full_name = post_dict[NOM_NAME_KEY]
            officer_position = post_dict[NOM_POSITION_KEY]
            speech = post_dict[NOM_SPEECH_KEY]
            facebook_link = post_dict[NOM_FACEBOOK_KEY]
            linkedin_link = post_dict[NOM_LINKEDIN_KEY]
            email_address = post_dict[NOM_EMAIL_KEY]
            discord_username = post_dict[NOM_DISCORD_USERNAME_KEY]
            if full_name != 'NONE':
                logger.info(
                    "[administration/views.py create_specified_election()] "
                    f"saved user full_name={full_name} officer_position={officer_position} "
                    f"speech={speech} facebook_link={facebook_link} linkedin_link="
                    f"{linkedin_link} email_address={email_address} discord_username"
                    f"={discord_username}"
                )
                nom = Nominee(
                    nomination_page=nomination_page,
                    name=full_name,
                    officer_position=officer_position,
                    speech=speech,
                    facebook=facebook_link,
                    linked_in=linkedin_link,
                    email=email_address,
                    discord=discord_username,
                    position=position_index
                )
                nom.save()

        return render(request, 'administration/create_election.html', context)
    return render(request, 'administration/create_election.html', context)


def save_nominees(post_dict, nomination_page, position_index):
    for i in range(len(post_dict[NOM_NAME_KEY])):
        full_name = post_dict[NOM_NAME_KEY][i]
        officer_position = post_dict[NOM_POSITION_KEY][i]
        speech = post_dict[NOM_SPEECH_KEY][i]
        facebook_link = post_dict[NOM_FACEBOOK_KEY][i]
        linkedin_link = post_dict[NOM_LINKEDIN_KEY][i]
        email_address = post_dict[NOM_EMAIL_KEY][i]
        discord_username = post_dict[NOM_DISCORD_USERNAME_KEY][i]
        logger.info(
            "[administration/views.py save_nominees()] saved user "
            f"full_name={full_name} officer_position={officer_position} speech={speech}"
            f" facebook_link={facebook_link} linkedin_link={linkedin_link} "
            f"email_address={email_address} discord_username={discord_username}"
        )
        if full_name != 'NONE':
            nom = Nominee(
                nomination_page=nomination_page,
                name=full_name,
                officer_position=officer_position,
                speech=speech,
                facebook=facebook_link,
                linked_in=linkedin_link,
                email=email_address,
                discord=discord_username,
                position=position_index
            )
            nom.save()
        else:
            logger.info(
                "[administration/views.py save_nominees()] skipping saving user "
                f"full_name={full_name} officer_position={officer_position} speech={speech} "
                f"facebook_link={facebook_link} linkedin_link={linkedin_link} "
                f"email_address={email_address}  discord_username={discord_username}"
            )


def create_or_update_specified_election_with_provided_json(request):
    logger.info(
        "[administration/views.py create_or_update_specified_election_with_provided_json()] "
        f"[create_or_update_specified_election_with_provided_json] request.POST={request.POST}"
    )
    groups = list(request.user.groups.values_list('name', flat=True))
    context = {
        'tab': 'administration',
        'authenticated': request.user.is_authenticated,
        'Officer': ('Officer' in groups),
        'ElectionOfficer': ('ElectionOfficer' in groups),
        'Staff': request.user.is_staff,
        'Username': request.user.username,
        'URL_ROOT': settings.URL_ROOT
    }
    if not ('ElectionOfficer' in groups or request.user.is_staff or 'Officer' in groups):
        return render(request, 'administration/invalid_access.html', context)
    if JSON_INPUT_POST_KEY in request.POST:
        logger.info(
            "[administration/views.py create_or_update_specified_election_with_provided_json()] "
            "creating new election"
        )
        post_dict = parser.parse(request.POST.urlencode())
        post_dict = json.loads(request.POST['input_json'])
        logger.info(
            "[administration/views.py create_or_update_specified_election_with_provided_json()] "
            f"post_dict={post_dict}"
        )
        nomination_page = get_nomination_page_json(json.loads(request.POST['input_json']))
        # post_dict = parser.parse(request.POST.urlencode())
        logger.info(
            "[administration/views.py create_or_update_specified_election_with_provided_json()] "
            f"post_dict={post_dict}"
        )
        logger.info(
            "[administration/views.py create_or_update_specified_election_with_provided_json()] "
            f"full_name={post_dict[ELECTION_NOMINEES_KEY]} len = {len(post_dict[ELECTION_NOMINEES_KEY])}"
        )
        save_nominees_from_json(post_dict[ELECTION_NOMINEES_KEY], nomination_page)

        return render(request, 'administration/create_election_json.html', context)
    return render(request, 'administration/create_election_json.html', context)


def get_nomination_page_json(input_json):
    dt = datetime.datetime.strptime(f"{input_json[ELECTION_DATE_KEY]}", '%Y-%m-%d %H:%M')
    slug = f"{dt.strftime('%Y-%m-%d')}-{input_json[ELECTION_TYPE_KEY]}"
    NominationPage.objects.filter(
        slug=slug,
    ).delete()

    nomination_page = NominationPage(
        slug=slug,
        election_type=input_json[ELECTION_TYPE_KEY],
        date=dt,
        websurvey=input_json[ELECTION_WEBSURVEY_LINK_KEY]
    )
    nomination_page.save()
    logger.info(f"[administration/views.py get_nomination_page_json()] nomination_page {nomination_page} created")
    return nomination_page


def save_nominees_from_json(nominees, nomination_page):
    position_index = 0
    for nominee in nominees:
        full_name = nominee[NOM_NAME_KEY]
        officer_position = nominee[NOM_POSITION_KEY]
        speech = nominee[NOM_SPEECH_KEY]
        facebook_link = nominee[NOM_FACEBOOK_KEY]
        linkedin_link = nominee[NOM_LINKEDIN_KEY]
        email_address = nominee[NOM_EMAIL_KEY]
        discord_username = nominee[NOM_DISCORD_USERNAME_KEY]
        logger.info(
            "[administration/views.py save_nominees_from_json()] saved user "
            f"full_name={full_name} officer_position={officer_position} speech={speech} "
            f"facebook_link={facebook_link} linkedin_link={linkedin_link} email_address="
            f"{email_address}  discord_username={discord_username}"
        )
        nom = Nominee(
            nomination_page=nomination_page,
            name=full_name,
            officer_position=officer_position,
            speech=speech,
            facebook=facebook_link,
            linked_in=linkedin_link,
            email=email_address,
            discord=discord_username,
            position=position_index
        )
        nom.save()
        position_index += 1


# displays page that allows the user to select the election and what action they want to perform on the election


def select_election_to_update(request):
    groups = list(request.user.groups.values_list('name', flat=True))
    context = {
        'tab': 'administration',
        'authenticated': request.user.is_authenticated,
        'Officer': ('Officer' in groups),
        'ElectionOfficer': ('ElectionOfficer' in groups),
        'Staff': request.user.is_staff,
        'Username': request.user.username,
        'URL_ROOT': settings.URL_ROOT
    }
    if not ('ElectionOfficer' in groups or request.user.is_staff or 'Officer' in groups):
        return render(request, 'administration/invalid_access.html', context)
    elections = NominationPage.objects.all().order_by('-id')
    context.update({'elections': elections})
    return render(request, 'administration/select_election.html', context)


# calls the function that does the action that was requred by the user on select_election.html page
# that the above function displayes for the user


def determine_election_action(request):
    logger.info(f"[administration/views.py determine_election_action()] request.POST={request.POST}")
    groups = list(request.user.groups.values_list('name', flat=True))
    context = {
        'tab': 'administration',
        'authenticated': request.user.is_authenticated,
        'Officer': ('Officer' in groups),
        'ElectionOfficer': ('ElectionOfficer' in groups),
        'Staff': request.user.is_staff,
        'Username': request.user.username,
        'URL_ROOT': settings.URL_ROOT
    }
    if not ('ElectionOfficer' in groups or request.user.is_staff or 'Officer' in groups):
        return render(request, 'administration/invalid_access.html', context)
    if 'action' in request.POST:
        if request.POST['action'] == DELETE_ACTION_POST_KEY and ELECTION_ID_KEY in request.POST:
            return delete_selected_election(request.POST[ELECTION_ID_KEY])
        elif request.POST['action'] == UPDATE_ACTION_POST_KEY and ELECTION_ID_KEY in request.POST:
            return display_selected_election_for_updating(request, request.POST[ELECTION_ID_KEY])
        elif request.POST['action'] == UPDATE_WITH_JSON_ACTION_POST_KEY and ELECTION_ID_KEY in request.POST:
            return display_selected_election_json_for_updating(request, request.POST[ELECTION_ID_KEY])
        else:
            logger.info(
                "[administration/views.py determine_election_action()] incorrect action detected, "
                "returning /administration/elections/select_election"
            )
            return HttpResponseRedirect(f"{settings.URL_ROOT}administration/elections/select_election")
    else:
        logger.info(
            "[administration/views.py determine_election_action()] action "
            "is not detected, returning /administration/elections/select_election"
        )
        return HttpResponseRedirect(f"{settings.URL_ROOT}administration/elections/select_election")


def delete_selected_election(election_id):
    NominationPage.objects.filter(slug=election_id).delete()
    return HttpResponseRedirect(f"{settings.URL_ROOT}administration/elections/select_election")


def display_selected_election_for_updating(request, election_id):
    groups = list(request.user.groups.values_list('name', flat=True))
    election = NominationPage.objects.get(slug=election_id)
    nominees = [nominee for nominee in Nominee.objects.all().filter(nomination_page=election)]
    nominees.sort(key=lambda x: x.position, reverse=True)
    context = {
        'tab': 'administration',
        'authenticated': request.user.is_authenticated,
        'nominees': nominees,
        'election': election,
        'date': election.date.strftime("%Y-%m-%d"),
        'time': election.date.strftime("%H:%M"),
        'election_type': election.election_type,
        'websurvey': election.websurvey,
        'Officer': ('Officer' in groups),
        'ElectionOfficer': ('ElectionOfficer' in groups),
        'Staff': request.user.is_staff,
        'Username': request.user.username,
        'URL_ROOT': settings.URL_ROOT
    }
    return render(request, 'administration/update_election.html', context)


def display_selected_election_json_for_updating(request, election_id):
    groups = list(request.user.groups.values_list('name', flat=True))
    election = NominationPage.objects.get(slug=election_id)
    nominees = [nominee for nominee in Nominee.objects.all().filter(nomination_page=election)]
    nominees.sort(key=lambda x: x.position, reverse=True)
    election_dict = {}
    election_dict[ELECTION_TYPE_KEY] = election.election_type
    election_dict[ELECTION_DATE_KEY] = election.date.strftime("%Y-%m-%d %H:%M")
    election_dict[ELECTION_WEBSURVEY_LINK_KEY] = election.websurvey
    election_dict[ELECTION_NOMINEES_KEY] = []
    for nominee in nominees:
        nom = {}
        nom[NOM_NAME_KEY] = nominee.name
        nom[NOM_POSITION_KEY] = nominee.officer_position
        nom[NOM_SPEECH_KEY] = nominee.speech
        nom[NOM_FACEBOOK_KEY] = nominee.facebook
        nom[NOM_LINKEDIN_KEY] = nominee.linked_in
        nom[NOM_EMAIL_KEY] = nominee.email
        nom[NOM_DISCORD_USERNAME_KEY] = nominee.discord
        election_dict[ELECTION_NOMINEES_KEY].append(nom)
    context = {
        'tab': 'administration',
        'authenticated': request.user.is_authenticated,
        'election_dict': json.dumps(election_dict),
        'Officer': ('Officer' in groups),
        'ElectionOfficer': ('ElectionOfficer' in groups),
        'Staff': request.user.is_staff,
        'Username': request.user.username,
        'URL_ROOT': settings.URL_ROOT
    }
    return render(request, 'administration/update_election_json.html', context)


# deletes the election and recreates it with the nominees that the user has specified


def update_specified_election(request):
    groups = list(request.user.groups.values_list('name', flat=True))
    context = {
        'tab': 'administration',
        'authenticated': request.user.is_authenticated,
        'Officer': ('Officer' in groups),
        'ElectionOfficer': ('ElectionOfficer' in groups),
        'Staff': request.user.is_staff,
        'Username': request.user.username,
        'URL_ROOT': settings.URL_ROOT
    }
    if not ('ElectionOfficer' in groups or request.user.is_staff or 'Officer' in groups):
        return render(request, 'administration/invalid_access.html', context)
    if ELECTION_TYPE_KEY in request.POST and ELECTION_DATE_POST_KEY in request.POST \
            and ELECTION_TIME_POST_KEY in request.POST and ELECTION_WEBSURVEY_LINK_KEY in request.POST:
        nomination_page = get_nomination_page(request.POST)
        post_dict = parser.parse(request.POST.urlencode())
        position_index = 0
        if (len(post_dict[NOM_NAME_KEY][0]) > 1):
            save_nominees(post_dict, nomination_page, position_index)
            position_index += 1
        else:
            full_name = post_dict[NOM_NAME_KEY]
            officer_position = post_dict[NOM_POSITION_KEY]
            speech = post_dict[NOM_SPEECH_KEY]
            facebook_link = post_dict[NOM_FACEBOOK_KEY]
            linkedin_link = post_dict[NOM_LINKEDIN_KEY]
            email_address = post_dict[NOM_EMAIL_KEY]
            discord_username = post_dict[NOM_DISCORD_USERNAME_KEY]
            if full_name != 'NONE':
                logger.info(
                    "[administration/views.py update_specified_election()] "
                    f"saved user full_name={full_name} officer_position={officer_position} "
                    f"speech={speech} facebook_link={facebook_link} linkedin_link={linkedin_link} "
                    f"email_address={email_address}  discord_username={discord_username}")
                nom = Nominee(
                    nomination_page=nomination_page,
                    name=full_name,
                    officer_position=officer_position,
                    speech=speech,
                    facebook=facebook_link,
                    linked_in=linkedin_link,
                    email=email_address,
                    discord=discord_username,
                    position=position_index
                )
                nom.save()

        return HttpResponseRedirect(f"{settings.URL_ROOT}administration/elections/select_election")
    return HttpResponseRedirect(f"{settings.URL_ROOT}administration/elections/select_election")


def get_nomination_page(request):
    dt = datetime.datetime.strptime(
        f"{request[ELECTION_DATE_POST_KEY]} {request[ELECTION_TIME_POST_KEY]}",
        '%Y-%m-%d %H:%M'
    )
    slug = f"{dt.strftime('%Y-%m-%d')}-{request[ELECTION_TYPE_KEY]}"
    NominationPage.objects.filter(
        slug=slug
    ).delete()

    nomination_page = NominationPage(
        slug=slug,
        election_type=request[ELECTION_TYPE_KEY],
        date=dt,
        websurvey=request[ELECTION_WEBSURVEY_LINK_KEY]
    )
    nomination_page.save()
    logger.info(f"[administration/views.py get_nomination_page()] nomination_page {nomination_page} created")
    return nomination_page
