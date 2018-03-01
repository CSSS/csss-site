from django.shortcuts import render

def index(request):
	print("WiCS index")
	return render(request, 'associated_dsus_and_clubs/wics.html')

def esss(request):
	print("esss index")
	return render(request, 'associated_dsus_and_clubs/esss.html')

def mechs(request):
	print("mechs index")
	return render(request, 'associated_dsus_and_clubs/mechs.html')

def ssss(request):
	print("ssss index")
	return render(request, 'associated_dsus_and_clubs/ssss.html')

def WiE(request):
	print("WiE index")
	return render(request, 'associated_dsus_and_clubs/WiE.html')
# Create your views here.
