from django.shortcuts import render

# Create your views here.
from django.views import generic

from .models import NominationPage, Nominee
from datetime import datetime


def getNominees(request, slug):
    retrievedObj = NominationPage.objects.filter(slug = slug)
    if retrievedObj[0].datePublic <= datetime.now():
        print("time to vote")
        nominees = Nominee.objects.filter(nominationPage__slug = slug).all().order_by('Position')
        return render(request, 'elections/nominee_list.html', {'election': retrievedObj[0], 'tab': 'elections', 'nominees' : nominees})
    else:
        print("cant vote yet")
        return render(request, 'elections/nominee_list.html', {'tab': 'elections', 'nominees' : 'none'})
