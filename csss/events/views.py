from django.shortcuts import render

def index(request):
    context = {
        'tab': 'events',
        'authenticated' : request.user.is_authenticated,
    }
    return render(request, 'events/calendar.html', context)

def gm(request):
    context = {
        'tab': 'events',
        'authenticated' : request.user.is_authenticated,
    }
    return render(request, 'events/gm.html', context)

def board_games(request):
    context = {
        'tab': 'events',
        'authenticated' : request.user.is_authenticated,
    }
    return render(request, 'events/board_games.html', context)

def gameJam(request):
    context = {
        'tab': 'events',
        'authenticated' : request.user.is_authenticated,
    }
    return render(request, 'events/game_jam.html', context)

def froshWeek(request):
    context = {
        'tab': 'events',
        'authenticated' : request.user.is_authenticated,
    }
    return render(request, 'events/frosh_week.html', context)

# Create your views here.
