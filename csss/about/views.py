from django.shortcuts import render
from about.models import Officer

# Create your views here.

def index(request):
	print("who we are index")
	return render(request, 'about/who_we_are.html')

def listOfOfficers(request):
	print("list of officers index")
	officers = Officer.objects.all().filter()
	return render(request, 'about/list_of_officers.html', {'officers': officers})