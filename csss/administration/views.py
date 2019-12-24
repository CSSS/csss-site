from django.shortcuts import render

# Create your views here.
from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout
from django.http import HttpResponseRedirect

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

def modify_election(request):
    context = {
        'tab': 'administration',
        'authenticated' : request.user.is_authenticated,
    }
    return render(request, 'administration/elections.html', context)

def create_election(request):
    context = {
        'tab': 'administration',
        'authenticated' : request.user.is_authenticated,
    }
    return render(request, 'administration/create_election.html', context)

def submit_election(request):
    print(f"request.POST={request.POST}")
    election_date = request.POST['election_date']
    election_type = request.POST['election_type']
    public_date = request.POST['public_date']
    public_time = request.POST['public_time']
    websurvey_link = request.POST['websurvey']
    nomPage = NominationPage(
        type_of_election = election_type,
        slugDate = election_date,
        websurvey = websurvey_link

    )
    for i in range(len(request.POST['full_name'])):
        full_name = request.POST['full_name'][i]
        position = request.POST['position'][i]
        speech = request.POST['speech'][i]
        facebook_link = request.POST['facebook_link'][i]
        linkedin_link = request.POST['linkedin_link'][i]
        email_address = request.POST['email_address'][i]
        discord_username = request.POST['discord_username'][i]
    context = {
        'tab': 'administration',
        'authenticated' : request.user.is_authenticated,
    }
    return render(request, 'administration/create_election.html', context)

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
