from django.shortcuts import render

def index(request):
    groups = list(request.user.groups.values_list('name',flat = True))
    context = {
        'tab': '750_project',
        'authenticated' : request.user.is_authenticated,
        'Exec' : ('Exec' in groups),
        'ElectionOfficer' : ('ElectionOfficer' in groups),
        'Staff' : request.user.is_staff,
        'Username' : request.user.username
    }
    return render(request, '750_project/about_750.html', context)

def hacktime(request):
    groups = list(request.user.groups.values_list('name',flat = True))
    context = {
        'tab': '750_project',
        'authenticated' : request.user.is_authenticated,
        'Exec' : ('Exec' in groups),
        'ElectionOfficer' : ('ElectionOfficer' in groups),
        'Staff' : request.user.is_staff,
        'Username' : request.user.username
    }
    return render(request, '750_project/hacktime.html', context)

def devTools(request):
    groups = list(request.user.groups.values_list('name',flat = True))
    context = {
        'tab': '750_project',
        'authenticated' : request.user.is_authenticated,
        'Exec' : ('Exec' in groups),
        'ElectionOfficer' : ('ElectionOfficer' in groups),
        'Staff' : request.user.is_staff,
        'Username' : request.user.username
    }
    return render(request, '750_project/dev_tools.html', context)

def workshops(request):
    groups = list(request.user.groups.values_list('name',flat = True))
    context = {
        'tab': '750_project',
        'authenticated' : request.user.is_authenticated,
        'Exec' : ('Exec' in groups),
        'ElectionOfficer' : ('ElectionOfficer' in groups),
        'Staff' : request.user.is_staff,
        'Username' : request.user.username
    }
    return render( request, '750_project/workshops.html', context)

# Create your views here.
