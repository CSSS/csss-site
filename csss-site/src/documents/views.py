from django.shortcuts import render
from documents.models import Media, Event, Album
import datetime
import math
from django.conf import settings
import logging
logger = logging.getLogger('csss_site')


def index(request):
    groups = list(request.user.groups.values_list('name', flat=True))
    context = {
        'tab': 'documents',
        'authenticated': request.user.is_authenticated,
        'Officer': ('Officer' in groups),
        'ElectionOfficer': ('ElectionOfficer' in groups),
        'Staff': request.user.is_staff,
        'Username': request.user.username,
        'URL_ROOT': settings.URL_ROOT
    }
    return render(request, 'documents/constitution.html', context)


def policies(request):
    groups = list(request.user.groups.values_list('name', flat=True))
    context = {
        'tab': 'documents',
        'authenticated': request.user.is_authenticated,
        'Officer': ('Officer' in groups),
        'ElectionOfficer': ('ElectionOfficer' in groups),
        'Staff': request.user.is_staff,
        'Username': request.user.username,
        'URL_ROOT': settings.URL_ROOT
    }
    return render(request, 'documents/policies.html', context)


def events(request):
    groups = list(request.user.groups.values_list('name', flat=True))
    events = Event.objects.all().filter()
    albums = Album.objects.all().filter()
    context = {
        'events': events,
        'albums': albums,
        'tab': 'documents',
        'authenticated': request.user.is_authenticated,
        'Officer': ('Officer' in groups),
        'ElectionOfficer': ('ElectionOfficer' in groups),
        'Staff': request.user.is_staff,
        'Username': request.user.username,
        'URL_ROOT': settings.URL_ROOT
    }
    return render(request, 'documents/events.html', context)


def album(request):
    groups = list(request.user.groups.values_list('name', flat=True))
    current_page = request.GET.get('p', 'none')
    if current_page == 'none':
        current_page = 1
    else:
        current_page = int(current_page)

    request_path = request.path
    index_of_last_forward_slash = request_path.rfind('/')
    year = request_path[index_of_last_forward_slash+1:]
    date = datetime.datetime(int(year[0:4]), int(year[5:7]), int(year[8:10]))

    index_of_second_last_forward_slash = request_path[:index_of_last_forward_slash-1].rfind('/')
    name = request_path[index_of_second_last_forward_slash+1:index_of_last_forward_slash]

    album = Album.objects.get(date=date, name=name)

    medias = []
    full_medias = Media.objects.all().filter(album_link=album)
    number_of_medias = len(full_medias)
    index = 0
    lower_bound = (((current_page - 1) * 10) + 1)
    upper_bound = current_page * 10
    for media in full_medias:
        index += 1
        if (lower_bound <= index) and (index <= upper_bound):
            medias.append(media)

        if current_page == 1:
            previous_page = math.floor((number_of_medias / 10) + 1)
            next_page = 2
        elif current_page == math.floor((number_of_medias / 10) + 1):
            previous_page = current_page - 1
            next_page = 1
        else:
            previous_page = current_page - 1
            next_page = current_page + 1

    previous_button_link = request_path+'?p='+str(previous_page)
    next_button_link = request_path+'?p='+str(next_page)
    context = {
        'tab': 'documents',
        'authenticated': request.user.is_authenticated,
        'album': album,
        'nextButtonLink': next_button_link,
        'previousButtonLink': previous_button_link,
        'medias': medias,
        'Officer': ('Officer' in groups),
        'ElectionOfficer': ('ElectionOfficer' in groups),
        'Staff': request.user.is_staff,
        'Username': request.user.username,
        'URL_ROOT': settings.URL_ROOT
    }
    return render(request, 'documents/album.html', context)
