from django.shortcuts import render

def index(request):
    groups = list(request.user.groups.values_list('name',flat = True))
    context = {
        'tab': 'comp_sci_guide',
        'authenticated' : request.user.is_authenticated,
        'Exec' : ('Exec' in groups),
        'ElectionOfficer' : ('ElectionOfficer' in groups),
        'Staff' : request.user.is_staff,
        'Username' : request.user.username
    }
    return render(request, 'comp_sci_guide/course_map.html', context)

def software(request):
    groups = list(request.user.groups.values_list('name',flat = True))
    context = {
        'tab': 'comp_sci_guide',
        'authenticated' : request.user.is_authenticated,
        'Exec' : ('Exec' in groups),
        'ElectionOfficer' : ('ElectionOfficer' in groups),
        'Staff' : request.user.is_staff,
        'Username' : request.user.username
    }
    return render(request, 'comp_sci_guide/software.html', context)

def textbooks(request):
    groups = list(request.user.groups.values_list('name',flat = True))
    context = {
        'tab': 'comp_sci_guide',
        'authenticated' : request.user.is_authenticated,
        'Exec' : ('Exec' in groups),
        'ElectionOfficer' : ('ElectionOfficer' in groups),
        'Staff' : request.user.is_staff,
        'Username' : request.user.username
    }
    return render(request, 'comp_sci_guide/textbooks.html', context)

def courseReview(request):
    groups = list(request.user.groups.values_list('name',flat = True))
    context = {
        'tab': 'comp_sci_guide',
        'authenticated' : request.user.is_authenticated,
        'Exec' : ('Exec' in groups),
        'ElectionOfficer' : ('ElectionOfficer' in groups),
        'Staff' : request.user.is_staff,
        'Username' : request.user.username
    }
    return render(request, 'comp_sci_guide/course_reviews.html', context)
# Create your views here.
