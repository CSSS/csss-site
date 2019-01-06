from django.shortcuts import render

def index(request):
	print("WiCS index")
	return render(request, 'associated_dsus_and_clubs/wics.html', {'tab': 'associated_dsus_and_clubs'})

def esss(request):
	print("esss index")
	return render(request, 'associated_dsus_and_clubs/esss.html', {'tab': 'associated_dsus_and_clubs'})

def mechs(request):
	print("mechs index")
	return render(request, 'associated_dsus_and_clubs/mechs.html', {'tab': 'associated_dsus_and_clubs'})

def ssss(request):
	print("ssss index")
	return render(request, 'associated_dsus_and_clubs/ssss.html', {'tab': 'associated_dsus_and_clubs'})

def WiE(request):
	print("WiE index")
	return render(request, 'associated_dsus_and_clubs/WiE.html', {'tab': 'associated_dsus_and_clubs'})
# Create your views here.
