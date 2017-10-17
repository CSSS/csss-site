from django.shortcuts import render

def index(request):
	return render(request, 'personal/home.html')
# Create your views here.
