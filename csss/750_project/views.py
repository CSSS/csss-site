from django.shortcuts import render

def index(request):
    context = {
        'tab': '750_project',
        'authenticated' : request.user.is_authenticated,
    }
    return render(request, '750_project/about_750.html', context)

def hacktime(request):
    context = {
        'tab': '750_project',
        'authenticated' : request.user.is_authenticated,
    }
    return render(request, '750_project/hacktime.html', context)

def devTools(request):
    context = {
        'tab': '750_project',
        'authenticated' : request.user.is_authenticated,
    }
    return render(request, '750_project/dev_tools.html', context)

def workshops(request):
    context = {
        'tab': '750_project',
        'authenticated' : request.user.is_authenticated,
    }
    return render( request, '750_project/workshops.html', context)

# Create your views here.
