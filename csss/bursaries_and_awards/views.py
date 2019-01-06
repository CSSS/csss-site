from django.shortcuts import render

def index(request):
	print("bursaries and awards index")
	return render(request, 'bursaries_and_awards/index.html', {'tab': 'bursaries_and_awards'})
# Create your views here.
