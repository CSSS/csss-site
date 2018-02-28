from django.shortcuts import render

def index(request):
	print("who we are index")
	return render(request, 'about/who_we_are.html')

def listOfOfficers(request):
	print("list of officers index")
	return render(request, 'about/list_of_officers.html')
# Create your views here.
