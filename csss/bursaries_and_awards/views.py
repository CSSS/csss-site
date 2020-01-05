from django.shortcuts import render

def index(request):
    context = {
        'tab': 'bursaries_and_awards',
        'authenticated' : request.user.is_authenticated,
    }
    return render(request, 'bursaries_and_awards/index.html', context)
# Create your views here.
