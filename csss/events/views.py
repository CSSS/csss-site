from django.shortcuts import render

def index(request):
	print("calendar index")
	return render(request, 'events/calendar.html', {'tab': 'events'})

def gm(request):
	print("general meetings index")
	return render(request, 'events/gm.html', {'tab': 'events'})

def board_games(request):
	print("board games index")
	return render(request, 'events/board_games.html', {'tab': 'events'})

def gameJam(request):
	print("game jams index")
	return render(request, 'events/game_jam.html', {'tab': 'events'})

def froshWeek(request):
	print("frosh week index")
	return render(request, 'events/frosh_week.html', {'tab': 'events'})

# Create your views here.
