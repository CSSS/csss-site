from django.shortcuts import render

def index(request):
	print("bursaries and awards index")
	return render(request, 'bursaries_and_awards/index.html')
# Create your views here.
