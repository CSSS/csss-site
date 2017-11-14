from django.shortcuts import render

def index(request):
	return render(request, 'personal/home.html')

def contact(request):
	return render(request, 'personal/basic.html', {'content':['If you would like to contact me, please email me', 'csss-webmaster@sfu.ca']})
# Create your views here.
