import logging
logger = logging.getLogger('csss_site')
from django.shortcuts import render

def add_users_gdrive(request):
    logger.info(f"[administration/resource_management.py add_users_gdrive()] request.POST={request.POST}")
    groups = list(request.user.groups.values_list('name', flat=True))
    context = {
        'tab': 'administration',
        'authenticated': request.user.is_authenticated,
        'Exec': ('Exec' in groups),
        'ElectionOfficer': ('ElectionOfficer' in groups),
        'Staff': request.user.is_staff,
        'Username': request.user.username
    }
    if not (request.user.is_staff or 'Exec' in groups):
        return render(request, 'administration/invalid_access.html', context)

def remove_users_gdrive(request):
    logger.info(f"[administration/resource_management.py remove_users_gdrive()] request.POST={request.POST}")
    groups = list(request.user.groups.values_list('name', flat=True))
    context = {
        'tab': 'administration',
        'authenticated': request.user.is_authenticated,
        'Exec': ('Exec' in groups),
        'ElectionOfficer': ('ElectionOfficer' in groups),
        'Staff': request.user.is_staff,
        'Username': request.user.username
    }
    if not (request.user.is_staff or 'Exec' in groups):
        return render(request, 'administration/invalid_access.html', context)

def make_public_link_gdrive(request):
    logger.info(f"[administration/resource_management.py make_public_link_gdrive()] request.POST={request.POST}")
    groups = list(request.user.groups.values_list('name', flat=True))
    context = {
        'tab': 'administration',
        'authenticated': request.user.is_authenticated,
        'Exec': ('Exec' in groups),
        'ElectionOfficer': ('ElectionOfficer' in groups),
        'Staff': request.user.is_staff,
        'Username': request.user.username
    }
    if not (request.user.is_staff or 'Exec' in groups):
        return render(request, 'administration/invalid_access.html', context)

def remove_public_link_gdrive(request):
    logger.info(f"[administration/resource_management.py remove_public_link_gdrive()] request.POST={request.POST}")
    groups = list(request.user.groups.values_list('name', flat=True))
    context = {
        'tab': 'administration',
        'authenticated': request.user.is_authenticated,
        'Exec': ('Exec' in groups),
        'ElectionOfficer': ('ElectionOfficer' in groups),
        'Staff': request.user.is_staff,
        'Username': request.user.username
    }
    if not (request.user.is_staff or 'Exec' in groups):
        return render(request, 'administration/invalid_access.html', context)
