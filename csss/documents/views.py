from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from documents.models import Media, Event, Album, Picture, Video
import datetime
import math

import logging
logger = logging.getLogger('csss_site')

def index(request):
    context = {
        'tab': 'documents',
        'authenticated' : request.user.is_authenticated,
    }
    return render(request, 'documents/constitution.html', context)

def policies(request):
    context = {
        'tab': 'documents',
        'authenticated' : request.user.is_authenticated,
    }
    return render(request, 'documents/policies.html', context)

def events(request):
    events = Event.objects.all().filter()
    albums = Album.objects.all().filter()
    context = {
        'events': events,
        'albums': albums,
        'tab': 'documents',
        'authenticated' : request.user.is_authenticated,
    }
    return render(request, 'documents/events.html', context)

def album(request):
    currentPage=request.GET.get('p', 'none')
    if currentPage == 'none':
        currentPage = 1
    else:
        currentPage=int(currentPage)

    request_path = request.path
    indexOfLastForwardSlash=request_path.rfind('/')
    year=request_path[indexOfLastForwardSlash+1:]
    date=datetime.datetime(int(year[0:4]), int(year[5:7]), int(year[8:10]))

    indexOfSecondLastForwardSlash=request_path[:indexOfLastForwardSlash-1].rfind('/')
    name=request_path[indexOfSecondLastForwardSlash+1:indexOfLastForwardSlash]

    album = Album.objects.get(date=date, name=name)

    medias = []
    fullmedias = Media.objects.all().filter(album_link=album)
    numberOfMedias = len(fullmedias)
    index=0
    lowerBound = ( ( ( currentPage  - 1 ) * 10 ) + 1 )
    upperBound = currentPage * 10
    for media in fullmedias:
        index+=1
        if ( lowerBound <= index ) and ( index <= upperBound ):
            medias.append(media)

        if currentPage == 1:
            previousPage = math.floor((numberOfMedias / 10 ) + 1)
            nextPage = 2
        elif currentPage == math.floor((numberOfMedias / 10 ) + 1):
            previousPage = currentPage - 1
            nextPage = 1
        else:
            previousPage = currentPage - 1
            nextPage = currentPage + 1

    previousButtonLink=request_path+'?p='+str(previousPage)
    nextButtonLink=request_path+'?p='+str(nextPage)
    context = {
        'tab': 'documents',
        'authenticated' : request.user.is_authenticated,
        'album': album,
        'nextButtonLink':nextButtonLink,
        'previousButtonLink': previousButtonLink,
        'medias': medias,
    }
    return render(request, 'documents/album.html', context)
