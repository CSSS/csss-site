from django.shortcuts import render


def index(request):
    groups = list(request.user.groups.values_list('name', flat=True))
    context = {
        'tab': 'events',
        'authenticated': request.user.is_authenticated,
        'Exec': ('Exec' in groups),
        'ElectionOfficer': ('ElectionOfficer' in groups),
        'Staff': request.user.is_staff,
        'Username': request.user.username
    }
    return render(request, 'events/calendar.html', context)


def gm(request):
    groups = list(request.user.groups.values_list('name', flat=True))
    context = {
        'tab': 'events',
        'authenticated': request.user.is_authenticated,
        'Exec': ('Exec' in groups),
        'ElectionOfficer': ('ElectionOfficer' in groups),
        'Staff': request.user.is_staff,
        'Username': request.user.username
    }
    return render(request, 'events/gm.html', context)


def board_games(request):
    groups = list(request.user.groups.values_list('name', flat=True))
    context = {
        'tab': 'events',
        'authenticated': request.user.is_authenticated,
        'Exec': ('Exec' in groups),
        'ElectionOfficer': ('ElectionOfficer' in groups),
        'Staff': request.user.is_staff,
        'Username': request.user.username
    }
    return render(request, 'events/board_games.html', context)

def frosh_week(request):
    groups = list(request.user.groups.values_list('name', flat=True))
    context = {
        'tab': 'events',
        'authenticated': request.user.is_authenticated,
        'Exec': ('Exec' in groups),
        'ElectionOfficer': ('ElectionOfficer' in groups),
        'Staff': request.user.is_staff,
        'Username': request.user.username
    }
    return render(request, 'events/frosh_week.html', context)


def mountain_madness2020(request):
    groups = list(request.user.groups.values_list('name', flat=True))
    context = {
        'tab': 'events',
        'authenticated': request.user.is_authenticated,
        'Exec': ('Exec' in groups),
        'ElectionOfficer': ('ElectionOfficer' in groups),
        'Staff': request.user.is_staff,
        'Username': request.user.username
    }
    return render(request, 'events/mountain_madness2020.html', context)

# Create your views here.
