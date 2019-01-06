from django.shortcuts import render

def index(request):
	print("About 750 index")
	return render(request, '750_project/about_750.html', {'tab': '750_project'})

def hacktime(request):
	print("Hacktime index")
	return render(request, '750_project/hacktime.html', {'tab': '750_project'})

def devTools(request):
	print("dev tools index")
	return render(request, '750_project/dev_tools.html', {'tab': '750_project'})

def workshops(request):
	print("workshops index")
	return render( request, '750_project/workshops.html', {'tab': '750_project'})

# Create your views here.
