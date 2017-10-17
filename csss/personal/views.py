from django.shortcuts import render

def index(request):
	return render(requst, 'personal/home.html')
# Create your views here.
