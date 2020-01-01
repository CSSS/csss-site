from django.shortcuts import render

# Create your views here.
from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout
from django.http import HttpResponseRedirect

from elections.models import NominationPage, Nominee

from shopping.models import Merchandise

from querystring_parser import parser

import datetime
import json

NOM_NAME_KEY = 'name'
NOM_POSITION_KEY = 'exec_position'
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

MERCHANDISE_PICTURE_LINK_KEY = 'picture_link'
MERCHANDISE_NAME_KEY = 'merchandise'
MERCHANDISE_SIZE_KEY = 'size'
MERCHANDISE_COLOR_KEY = 'color'
MERCHANDISE_PRICE_KEY = 'price'

JSON_INPUT_POST_KEY = 'input_json'

def login(request):
    print(f"[login] request.POST={request.POST}")

    if 'username' in request.POST and 'password' in request.POST:
        username = request.POST['username']
        password = request.POST['password']
        print(f"username = {username}")
        print(f"password = {password}")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            dj_login(request, user)
            print("it was a successful login")
    print("it was an insuccessful login")
    return HttpResponseRedirect('/')

def logout(request):
    dj_logout(request)
    return HttpResponseRedirect('/')

def select_election_to_update(request):
    elections = NominationPage.objects.all().order_by('-id')
    context = {
        'tab': 'administration',
        'authenticated' : request.user.is_authenticated,
        'elections' : elections
    }
    return render(request, 'administration/select_election.html', context)

def determine_election_action(request):
    print(f"[determine_election_action] request.POST={request.POST}")
    if 'action' in request.POST:
        if request.POST['action'] == DELETE_ACTION_POST_KEY and ELECTION_ID_KEY in request.POST :
            return delete_selected_election(request.POST[ELECTION_ID_KEY])
        elif request.POST['action'] == UPDATE_ACTION_POST_KEY and ELECTION_ID_KEY in request.POST :
            return display_selected_election_for_updating(request, request.POST[ELECTION_ID_KEY])
        elif request.POST['action'] == UPDATE_WITH_JSON_ACTION_POST_KEY and ELECTION_ID_KEY in request.POST :
            return display_selected_election_json_for_updating(request, request.POST[ELECTION_ID_KEY])
        else:
            return HttpResponseRedirect('/administration/elections/select_election')
    else:
        return HttpResponseRedirect('/administration/elections/select_election')

def delete_selected_election(election_id):
    NominationPage.objects.filter(slug = election_id).delete()
    return HttpResponseRedirect('/administration/elections/select_election')

def display_selected_election_for_updating(request, election_id):
    election = NominationPage.objects.get(slug = election_id)
    nominees = [nominee for nominee in Nominee.objects.all().filter(nomination_page = election)]
    nominees.sort(key=lambda x: x.position, reverse=True)
    context = {
        'tab': 'administration',
        'authenticated' : request.user.is_authenticated,
        'nominees' : nominees,
        'election' : election,
        'date': election.date.strftime("%Y-%m-%d"),
        'time' : election.date.strftime("%H:%M"),
        'election_type': election.election_type,
        'websurvey' : election.websurvey
    }
    return render(request, 'administration/update_election.html', context)

def display_selected_election_json_for_updating(request, election_id):
    election = NominationPage.objects.get(slug = election_id)
    nominees = [nominee for nominee in Nominee.objects.all().filter(nomination_page = election)]
    nominees.sort(key= lambda x: x.position, reverse = True)
    election_dict = {}
    election_dict[ELECTION_TYPE_KEY] = election.election_type
    election_dict[ELECTION_DATE_KEY] = election.date.strftime("%Y-%m-%d %H:%M")
    election_dict[ELECTION_WEBSURVEY_LINK_KEY] = election.websurvey
    election_dict[ELECTION_NOMINEES_KEY] = []
    for nominee in nominees:
        nom = {}
        nom[NOM_NAME_KEY] = nominee.name
        nom[NOM_POSITION_KEY] = nominee.exec_position
        nom[NOM_SPEECH_KEY] = nominee.speech
        nom[NOM_FACEBOOK_KEY] = nominee.facebook
        nom[NOM_LINKEDIN_KEY] = nominee.linked_in
        nom[NOM_EMAIL_KEY] = nominee.email
        nom[NOM_DISCORD_USERNAME_KEY] = nominee.discord
        election_dict[ELECTION_NOMINEES_KEY].append(nom)
    context = {
        'tab' : 'administration',
        'authenticated' : request.user.is_authenticated,
        'election_dict': json.dumps(election_dict)
    }

    return render(request, 'administration/update_election_json.html', context)

def get_nomination_page(request):
    dt = datetime.datetime.strptime(f"{request[ELECTION_DATE_POST_KEY]} {request[ELECTION_TIME_POST_KEY]}", '%Y-%m-%d %H:%M')
    slug = f"{dt.strftime('%Y-%m-%d')}-{request[ELECTION_TYPE_KEY]}"
    NominationPage.objects.filter(
        slug = slug,
        election_type = request[ELECTION_TYPE_KEY],
        date = dt,
        websurvey = request[ELECTION_WEBSURVEY_LINK_KEY]
    ).delete()

    nomPage = NominationPage(
        slug = slug,
        election_type = request[ELECTION_TYPE_KEY],
        date = dt,
        websurvey = request[ELECTION_WEBSURVEY_LINK_KEY]
    )
    nomPage.save()
    print(f" nomPage {nomPage} created")
    return nomPage

def get_nomination_page_json(input_json):
    dt = datetime.datetime.strptime(f"{input_json[ELECTION_DATE_KEY]}", '%Y-%m-%d %H:%M')
    slug = f"{dt.strftime('%Y-%m-%d')}-{input_json[ELECTION_TYPE_KEY]}"
    NominationPage.objects.filter(
        slug = slug,
        election_type = input_json[ELECTION_TYPE_KEY],
        date = dt,
        websurvey = input_json[ELECTION_WEBSURVEY_LINK_KEY]
    ).delete()

    nomPage = NominationPage(
        slug = slug,
        election_type = input_json[ELECTION_TYPE_KEY],
        date = dt,
        websurvey = input_json[ELECTION_WEBSURVEY_LINK_KEY]
    )
    nomPage.save()
    print(f" nomPage {nomPage} created")
    return nomPage

def update_specified_election(request):
    context = {
        'tab': 'administration',
        'authenticated' : request.user.is_authenticated,
    }
    if ELECTION_TYPE_KEY in request.POST and ELECTION_DATE_POST_KEY in request.POST \
        and ELECTION_TIME_POST_KEY in request.POST and ELECTION_WEBSURVEY_LINK_KEY in request.POST:
        nomPage = get_nomination_page(request.POST)
        post_dict = parser.parse(request.POST.urlencode())
        position_index=0
        if (len(post_dict[NOM_NAME_KEY][0]) > 1):
            save_nominees(post_dict, nomPage, position_index)
            position_index+=1
        else:
            full_name = post_dict[NOM_NAME_KEY]
            exec_position = post_dict[NOM_POSITION_KEY]
            speech = post_dict[NOM_SPEECH_KEY]
            facebook_link = post_dict[NOM_FACEBOOK_KEY]
            linkedin_link = post_dict[NOM_LINKEDIN_KEY]
            email_address = post_dict[NOM_EMAIL_KEY]
            discord_username = post_dict[NOM_DISCORD_USERNAME_KEY]
            if full_name != 'NONE':
                print(
                    f"saved user full_name={full_name} exec_position={exec_position} speech={speech} facebook_link={facebook_link} "
                    "linkedin_link={linkedin_link} email_address={email_address}  discord_username={discord_username}")
                nom = Nominee(
                    nomination_page = nomPage,
                    name = full_name,
                    exec_position = exec_position,
                    speech = speech,
                    facebook = facebook_link,
                    linked_in = linkedin_link,
                    email = email_address,
                    discord = discord_username,
                    position = position_index
                )
                nom.save()

        return HttpResponseRedirect('/administration/elections/select_election')
    return HttpResponseRedirect('/administration/elections/select_election')

def create_specified_election(request):
    print(f"[create_specified_election] request.POST={request.POST}")
    context = {
        'tab': 'administration',
        'authenticated' : request.user.is_authenticated,
    }
    if ELECTION_TYPE_KEY in request.POST and ELECTION_DATE_POST_KEY in request.POST and \
        ELECTION_TIME_POST_KEY in request.POST and ELECTION_WEBSURVEY_LINK_KEY in request.POST:
        print("creating new election")
        if (request.POST[ELECTION_TYPE_KEY] == 'by_election'):
            election_type = "By-Election"
        elif (request.POST[ELECTION_TYPE_KEY] == 'general_election'):
            election_type = "General_Election"
        nomPage = get_nomination_page(request.POST)
        post_dict = parser.parse(request.POST.urlencode())
        print(f"post_dict={post_dict}")
        print(f"full_name={post_dict[NOM_NAME_KEY]} len = {len(post_dict[NOM_NAME_KEY])}")
        position_index=0
        if (len(post_dict[NOM_NAME_KEY][0]) > 1):
            save_nominees(post_dict, nomPage, position_index)
            position_index+=1
        else:
            full_name = post_dict[NOM_NAME_KEY]
            exec_position = post_dict[NOM_POSITION_KEY]
            speech = post_dict[NOM_SPEECH_KEY]
            facebook_link = post_dict[NOM_FACEBOOK_KEY]
            linkedin_link = post_dict[NOM_LINKEDIN_KEY]
            email_address = post_dict[NOM_EMAIL_KEY]
            discord_username = post_dict[NOM_DISCORD_USERNAME_KEY]
            if full_name != 'NONE':
                print(
                    f"saved user full_name={full_name} exec_position={exec_position} speech={speech} "
                    "facebook_link={facebook_link} linkedin_link={linkedin_link} email_address={email_address}"
                    "  discord_username={discord_username}")
                nom = Nominee(
                    nomination_page = nomPage,
                    name = full_name,
                    exec_position = exec_position,
                    speech = speech,
                    facebook = facebook_link,
                    linked_in = linkedin_link,
                    email = email_address,
                    discord = discord_username,
                    position=position_index
                )
                nom.save()

        return render(request, 'administration/create_election.html', context)
    return render(request, 'administration/create_election.html', context)

def save_nominees(post_dict, nomPage, position_index):
    for i in range(len(post_dict[NOM_NAME_KEY])):
        full_name = post_dict[NOM_NAME_KEY][i]
        exec_position = post_dict[NOM_POSITION_KEY][i]
        speech = post_dict[NOM_SPEECH_KEY][i]
        facebook_link = post_dict[NOM_FACEBOOK_KEY][i]
        linkedin_link = post_dict[NOM_LINKEDIN_KEY][i]
        email_address = post_dict[NOM_EMAIL_KEY][i]
        discord_username = post_dict[NOM_DISCORD_USERNAME_KEY][i]
        print(
            f"saved user full_name={full_name} exec_position={exec_position} speech={speech} "
            "facebook_link={facebook_link} linkedin_link={linkedin_link} email_address={email_address}"
            "  discord_username={discord_username}")
        if full_name != 'NONE':
            nom = Nominee(
                nomination_page = nomPage,
                name = full_name,
                exec_position = exec_position,
                speech = speech,
                facebook = facebook_link,
                linked_in = linkedin_link,
                email = email_address,
                discord = discord_username,
                position=position_index
            )
            nom.save()
        else:
            print(
                f"skipping saving user full_name={full_name} exec_position={exec_position} speech={speech} "
                "facebook_link={facebook_link} linkedin_link={linkedin_link} email_address={email_address}  "
                "discord_username={discord_username}")



def create_or_update_specified_election_with_provided_json(request):
    print(f"[create_or_update_specified_election_with_provided_json] request.POST={request.POST}")
    context = {
        'tab': 'administration',
        'authenticated' : request.user.is_authenticated,
    }
    if JSON_INPUT_POST_KEY in request.POST:
        print("creating new election")
        post_dict = parser.parse(request.POST.urlencode())
        post_dict = json.loads(request.POST['input_json'])
        print(f"post_dict={post_dict}")
        nomPage = get_nomination_page_json(json.loads(request.POST['input_json']))
        # post_dict = parser.parse(request.POST.urlencode())
        print(f"post_dict={post_dict}")
        print(f"full_name={post_dict[ELECTION_NOMINEES_KEY]} len = {len(post_dict[ELECTION_NOMINEES_KEY])}")
        save_nominees_from_json(post_dict[ELECTION_NOMINEES_KEY], nomPage)

        return render(request, 'administration/create_election_json.html', context)
    return render(request, 'administration/create_election_json.html', context)

def create_or_update_specified_election_with_provided_json(request):
    print(f"[create_or_update_specified_election_with_provided_json] request.POST={request.POST}")
    context = {
        'tab': 'administration',
        'authenticated' : request.user.is_authenticated,
    }
    if JSON_INPUT_POST_KEY in request.POST:
        print("creating new election")
        post_dict = parser.parse(request.POST.urlencode())
        post_dict = json.loads(request.POST['input_json'])
        print(f"post_dict={post_dict}")
        nomPage = get_nomination_page_json(json.loads(request.POST['input_json']))
        # post_dict = parser.parse(request.POST.urlencode())
        print(f"post_dict={post_dict}")
        print(f"full_name={post_dict[ELECTION_NOMINEES_KEY]} len = {len(post_dict[ELECTION_NOMINEES_KEY])}")
        position_index=0
        save_nominees_from_json(post_dict[ELECTION_NOMINEES_KEY], nomPage)

        return render(request, 'administration/create_election_json.html', context)
    return render(request, 'administration/create_election_json.html', context)

def save_nominees_from_json(nominees, nomPage):
    position_index=0
    for nominee in nominees:
        full_name = nominee[NOM_NAME_KEY]
        exec_position = nominee[NOM_POSITION_KEY]
        speech = nominee[NOM_SPEECH_KEY]
        facebook_link = nominee[NOM_FACEBOOK_KEY]
        linkedin_link = nominee[NOM_LINKEDIN_KEY]
        email_address = nominee[NOM_EMAIL_KEY]
        discord_username = nominee[NOM_DISCORD_USERNAME_KEY]
        print(
            f"saved user full_name={full_name} exec_position={exec_position} speech={speech} "
            "facebook_link={facebook_link} linkedin_link={linkedin_link} email_address={email_address}  "
            "discord_username={discord_username}")
        nom = Nominee(
            nomination_page = nomPage,
            name = full_name,
            exec_position = exec_position,
            speech = speech,
            facebook = facebook_link,
            linked_in = linkedin_link,
            email = email_address,
            discord = discord_username,
            position=position_index
        )
        nom.save()
        position_index+=1


def merch_list(request):
    merchandises = Merchandise.objects.all()
    context = {
        'tab': 'administration',
        'merchandises': merchandises,
        'authenticated' : request.user.is_authenticated,
    }
    return render(request, 'administration/merchandise_list.html', context)

MERCHANDISE_PICTURE_LINK_KEY = 'picture_link'
MERCHANDISE_NAME_KEY = 'merchandise'
MERCHANDISE_SIZE_KEY = 'size'
MERCHANDISE_COLOR_KEY = 'color'
MERCHANDISE_PRICE_KEY = 'price'

from io import StringIO
import csv

def merch_update(request):
    print(f"[administration/views.py merch_update()]")
    print(f"request.POST={request.POST}")
    if MERCHANDISE_PICTURE_LINK_KEY in request.POST and MERCHANDISE_NAME_KEY in request.POST and MERCHANDISE_SIZE_KEY in request.POST \
        and MERCHANDISE_COLOR_KEY in request.POST and MERCHANDISE_PRICE_KEY in request.POST:
        post_dict = parser.parse(request.POST.urlencode())
        print(f"post_dict = {post_dict}")
        print(f"post_dict[MERCHANDISE_NAME_KEY] = {post_dict[MERCHANDISE_NAME_KEY]}")
        print(f"len(post_dict[MERCHANDISE_NAME_KEY]) = {len(post_dict[MERCHANDISE_NAME_KEY])}")
        if len(post_dict[MERCHANDISE_NAME_KEY][0]) == 1: # only one merchandise was added
            print(f"only 1 merchandise {post_dict[MERCHANDISE_NAME_KEY]} was added")
            print(f"price = {post_dict[MERCHANDISE_NAME_KEY]}, image_absolute_file_path = {post_dict[MERCHANDISE_PICTURE_LINK_KEY]}")
            print(f"color = {post_dict[MERCHANDISE_COLOR_KEY]}, size = {post_dict[MERCHANDISE_SIZE_KEY]}")
            merch, created = Merchandise.objects.get_or_create(
                image_absolute_file_path= post_dict[MERCHANDISE_PICTURE_LINK_KEY],
                merchandise_type= post_dict[MERCHANDISE_NAME_KEY],
                price= post_dict[MERCHANDISE_PRICE_KEY],
            )
            feat, created = Feature.objects.get_or_create(
                merchandise_key = merch,
                feature_type = MERCHANDISE_COLOR_KEY
            )
            colors = [color.strip() for row in csv.reader(StringIO(post_dict[MERCHANDISE_COLOR_KEY]), delimiter=',') for color in row]
            for color in colors:
                spec, created = Feature.objects.get_or_create(
                    merchandise_key
            sizes = [size.strip() for row in csv.reader(StringIO(post_dict[MERCHANDISE_SIZE_KEY]), delimiter=',') for size in row]
            print(f"colors={colors}")
            print(f"sizes={sizes}")
            return HttpResponseRedirect('/administration/merch/list')

        else:
            for i in range(len(post_dict[MERCHANDISE_NAME_KEY])):
                print(f"post_dict[{MERCHANDISE_NAME_KEY}][{i}] == {post_dict[MERCHANDISE_NAME_KEY][i]}")

def order_list(request):
    object_list = Merchandise.objects.all()
    context = {
        'tab': 'administration',
        'object_list': object_list,
        'authenticated' : request.user.is_authenticated,
    }
    return render(request, 'administration/merchandise_list.html', context)
