from django.shortcuts import render

def index(request):
	print("calendar index")
	return render(request, 'events/calendar.html')

def gm(request):
	print("general meetings index")
	return render(request, 'events/gm.html')

def hacktime(request):
	print("hacktime index")
	return render(request, 'events/hacktime.html')

def gameJam(request):
	print("game jams index")
	return render(request, 'events/game_jam.html')

def froshWeek(request):
	print("frosh week index")
	return render(request, 'events/frosh_week.html')

def workshops(request):
	print("workshops index")
	return render(request, 'events/workshops.html')
# Create your views here.
