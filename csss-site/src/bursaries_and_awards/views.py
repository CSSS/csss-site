from django.shortcuts import render
from django.conf import settings

def index(request):
    groups = list(request.user.groups.values_list('name', flat=True))
    context = {
        'tab': 'bursaries_and_awards',
        'authenticated': request.user.is_authenticated,
        'Exec': ('Exec' in groups),
        'ElectionOfficer': ('ElectionOfficer' in groups),
        'Staff': request.user.is_staff,
        'Username': request.user.username,
        'URL_ROOT': "/"+settings.URL_ROOT
    }
    return render(request, 'bursaries_and_awards/index.html', context)
