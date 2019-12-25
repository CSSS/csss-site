from django.shortcuts import render

# Create your views here.
from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout
from django.http import HttpResponseRedirect

from elections.models import NominationPage, Nominee

from querystring_parser import parser

import datetime

def login(request):
    print(f"request.POST={request.POST}")

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


def exec(request):
    context = {
        'tab': 'administration',
        'authenticated' : request.user.is_authenticated,
    }
    return render(request, 'administration/exec.html', context)

def select_election(request):
    elections = NominationPage.objects.all().order_by('-id') 
    context = {
        'tab': 'administration',
        'authenticated' : request.user.is_authenticated,
        'elections' : elections
    }
    return render(request, 'administration/select_election.html', context)

def create_election(request):
    print(f"request.POST={request.POST}")
    context = {
        'tab': 'administration',
        'authenticated' : request.user.is_authenticated,
    }
    if 'election_type' in request.POST and 'public_date' in request.POST and 'public_time' in request.POST and 'websurvey' in request.POST:
        print("creating new election")
        if (request.POST['election_type'] == 'by_election'):
            election_type = "By-Election"
        elif (request.POST['election_type'] == 'general_election'):
            election_type = "General Election"
        public_date = request.POST['public_date']
        public_time = request.POST['public_time']
        websurvey_link = request.POST['websurvey']
        print(f"public_date={public_date} public_time={public_time}")
        dt = datetime.datetime.strptime("{} {}".format(public_date, public_time), '%Y-%m-%d %H:%M')
        nomPage = NominationPage(
            slug = "{}-{}".format(public_date,request.POST['election_type']),
            type_of_election = election_type,
            datePublic = dt,
            websurvey = websurvey_link
        )
        nomPage.save()
        post_dict = parser.parse(request.POST.urlencode())
        print(f"post_dict={post_dict}")
        print(f"full_name={post_dict['full_name']} len = {len(post_dict['full_name'])}")
        if (len(post_dict['full_name'][0]) > 1):
            for i in range(len(post_dict['full_name'])):
                full_name = post_dict['full_name'][i]
                position = post_dict['position'][i]
                speech = post_dict['speech'][i]
                facebook_link = post_dict['facebook_link'][i]
                linkedin_link = post_dict['linkedin_link'][i]
                email_address = post_dict['email_address'][i]
                discord_username = post_dict['discord_username'][i]
                print(f"saved user full_name={full_name} position={position} speech={speech} facebook_link={facebook_link} linkedin_link={linkedin_link} email_address={email_address}  discord_username={discord_username}")
                nom = Nominee(
                    nominationPage = nomPage,
                    name = full_name,
                    Position = position,
                    Speech = speech,
                    Facebook = facebook_link,
                    LinkedIn = linkedin_link,
                    Email = email_address,
                    Discord_Username = discord_username
                )
                nom.save()
        else:
            full_name = post_dict['full_name']
            position = post_dict['position']
            speech = post_dict['speech']
            facebook_link = post_dict['facebook_link']
            linkedin_link = post_dict['linkedin_link']
            email_address = post_dict['email_address']
            discord_username = post_dict['discord_username']
            print(f"saved user full_name={full_name} position={position} speech={speech} facebook_link={facebook_link} linkedin_link={linkedin_link} email_address={email_address}  discord_username={discord_username}")
            nom = Nominee(
                nominationPage = nomPage,
                name = full_name,
                Position = position,
                Speech = speech,
                Facebook = facebook_link,
                LinkedIn = linkedin_link,
                Email = email_address,
                Discord_Username = discord_username
            )
            nom.save()
           
        return render(request, 'administration/create_election.html', context)
    return render(request, 'administration/create_election.html', context)

def delete_election(election_id):
    NominationPage.objects.filter(slug = election_id).delete()
    return HttpResponseRedirect('/')

def modify_election(request, election_id):
    print(f"[modify_election] election_id={election_id}")
    election = NominationPage.objects.get(slug = election_id)
    print(f"[modify_election] election={election}")
    retrievedObjects = Nominee.objects.all().filter(nominationPage = election)
    print(f"[modify_election] retrievedObjects={retrievedObjects}")
    nominees = [nominee for nominee in retrievedObjects]
    print(f"[modify_election] nominees={nominees}")
    nominees.sort(key=lambda x: x.Position, reverse=True)
    date = election.datePublic.strftime("%Y-%m-%d")
    time = election.datePublic.strftime("%H:%M")
    print(f"[modify_election] election.type_of_election={election.type_of_election}")
    context = {
        'tab': 'administration',
        'authenticated' : request.user.is_authenticated,
        'nominees' : nominees,
        'election' : election,
        'date': date,
        'time' : time,
        'type_of_election': election.type_of_election
    }
    return render(request, 'administration/modify_election.html', context)



def determine_election_action(request):
    print(f"[determine_election_action] request.POST={request.POST}")
    if 'action' in request.POST:
        if request.POST['action'] == 'delete':
            delete_election(request.POST['election_id'])
        elif request.POST['action'] == 'Modify':
            return modify_election(request, request.POST['election_id'])
        else:
            return HttpResponseRedirect('/')
    else:
        return HttpResponseRedirect('/')
        context = {
        'tab': 'administration',
        'authenticated' : request.user.is_authenticated,
    }
    return render(request, 'administration/select_election.html', context)


def elections(request):
    context = {
        'tab': 'administration',
        'authenticated' : request.user.is_authenticated,
    }
    return render(request, 'administration/election.html', context)

def merch(request):
    context = {
        'tab': 'administration',
        'authenticated' : request.user.is_authenticated,
    }
    return render(request, 'administration/merch.html', context)

def post(request):
    context = {
        'tab': 'administration',
        'authenticated' : request.user.is_authenticated,
    }
    return render(request, 'administration/post.html', context)

def fileUpload(request):
    context = {
        'tab': 'administration',
        'authenticated' : request.user.is_authenticated,
    }
    return render(request, 'administration/fileUpload.html', context)
