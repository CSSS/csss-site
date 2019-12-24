from django.shortcuts import render

def index(request):
    print("calendar index")
    context = {
        'tab': 'events',
        'authenticated' : request.user.is_authenticated,
    }
    return render(request, 'events/calendar.html', context)

def gm(request):
    print("general meetings index")
    context = {
        'tab': 'events',
        'authenticated' : request.user.is_authenticated,
    }
    return render(request, 'events/gm.html', context)

def board_games(request):
    print("board games index")
    context = {
        'tab': 'events',
        'authenticated' : request.user.is_authenticated,
    }
    return render(request, 'events/board_games.html', context)

def gameJam(request):
    print("game jams index")
    context = {
        'tab': 'events',
        'authenticated' : request.user.is_authenticated,
    }
    return render(request, 'events/game_jam.html', context)

def froshWeek(request):
    print("frosh week index")
    context = {
        'tab': 'events',
        'authenticated' : request.user.is_authenticated,
    }
    return render(request, 'events/frosh_week.html', context)

# Create your views here.
