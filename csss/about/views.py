from django.shortcuts import render
from about.models import Officer

import datetime
# Create your views here.

def index(request):
	print("who we are index")
	return render(request, 'about/who_we_are.html', {'tab': 'about'})

def listOfOfficers(request):
    print("list of officers index")
    officers = Officer.objects.all().filter()
    now = datetime.datetime.now()
    termActive = (now.year*10) + int(now.month / 4)
    return render(request, 'about/list_of_officers.html', {'officers': officers, 'tab': 'about', 'termActive' : termActive})
