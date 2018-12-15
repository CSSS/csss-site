from django.shortcuts import render

def index(request):
	print("calendar index")
	return render(request, 'events/calendar.html')

def gm(request):
	print("general meetings index")
	return render(request, 'events/gm.html')

def board_games(request):
	print("board games index")
	return render(request, 'events/board_games.html')

def gameJam(request):
	print("game jams index")
	return render(request, 'events/game_jam.html')

def froshWeek(request):
	print("frosh week index")
	return render(request, 'events/frosh_week.html')

# Create your views here.
