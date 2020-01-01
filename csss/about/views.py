from django.shortcuts import render
from about.models import Officer

import datetime
# Create your views here.

def index(request):
    print("who we are index")
    context = {
        'tab': 'about',
        'authenticated' : request.user.is_authenticated,
    }
    return render(request, 'about/who_we_are.html', context)

def listOfOfficers(request):
    print("list of officers index")
    officers = Officer.objects.all().filter()
    now = datetime.datetime.now()
    termActive = (now.year*10) + int(now.month / 4)
    context = {
        'tab': 'about',
        'authenticated' : request.user.is_authenticated,
        'officers': officers,
        'termActive' : termActive,
    }
    return render(request, 'about/list_of_officers.html', context)
