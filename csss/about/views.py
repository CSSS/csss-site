from django.shortcuts import render

def index(request):
	print("who we are index")
	return render(request, 'about/who_we_are.html')

def listOfOfficers(request):
	print("list of officers index")
	return render(request, 'about/list_of_officers.html')
# Create your views here.

def fall_2017(request):
  print("fall_2017 index")
  return render(request, 'about/fall_2017.html')

def spring_2018(request):
  print("spring_2018 index")
  return render(request, 'about/spring_2018.html')

def summer_2017(request):
  print("summer_2017 index")
  return render(request, 'about/summer_2017.html')

def spring_2017(request):
  print("spring_2017 index")
  return render(request, 'about/spring_2017.html')