from django.shortcuts import render


def software(request):
    groups = list(request.user.groups.values_list('name', flat=True))
    context = {
        'tab': 'comp_sci_guide',
        'authenticated': request.user.is_authenticated,
        'Exec': ('Exec' in groups),
        'ElectionOfficer': ('ElectionOfficer' in groups),
        'Staff': request.user.is_staff,
        'Username': request.user.username
    }
    return render(request, 'comp_sci_guide/software.html', context)
