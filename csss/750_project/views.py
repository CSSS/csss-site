from django.shortcuts import render

def index(request):
	print("About 750 index")
	return render(request, '750_project/about_750.html')

def hacktime(request):
	print("Hacktime index")
	return render(request, '750_project/hacktime.html')

def devTools(request):
	print("dev tools index")
	return render(request, '750_project/dev_tools.html')

def workshops(request):
	print("workshops index")
	return render( request, '750_project/workshops.html')

# Create your views here.
