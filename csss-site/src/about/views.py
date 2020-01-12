from django.shortcuts import render
from about.models import Term, Officer, AnnouncementEmailAddress
from administration.models import OfficerUpdatePassphrase

# Create your views here.
from querystring_parser import parser
import datetime
from django.http import HttpResponseRedirect
from io import StringIO
import csv
import logging
logger = logging.getLogger('csss_site')


def index(request):
    groups = list(request.user.groups.values_list('name', flat=True))
    context = {
        'tab': 'about',
        'authenticated': request.user.is_authenticated,
        'Exec': ('Exec' in groups),
        'ElectionOfficer': ('ElectionOfficer' in groups),
        'Staff': request.user.is_staff,
        'Username': request.user.username
    }
    return render(request, 'about/who_we_are.html', context)


def list_of_officers(request):
    groups = list(request.user.groups.values_list('name', flat=True))
    officers = Officer.objects.all().filter()
    now = datetime.datetime.now()
    term_active = (now.year*10)
    if (int(now.month) <= 4):
        term_active += 1
    elif (int(now.month) <= 8):
        term_active += 2
    else:
        term_active += 3
    terms = Term.objects.all().order_by('-term_number')
    context = {
        'tab': 'about',
        'authenticated': request.user.is_authenticated,
        'officers': officers,
        'term_active': term_active,
        'terms': terms,
        'Exec': ('Exec' in groups),
        'ElectionOfficer': ('ElectionOfficer' in groups),
        'Staff': request.user.is_staff,
        'Username': request.user.username
    }
    return render(request, 'about/list_of_officers.html', context)


def input_exec_info(request):
    logger.info(f"[about/views.py input_exec_info()] request.GET={request.GET}")
    groups = list(request.user.groups.values_list('name', flat=True))
    context = {}
    get_keys = ['term', 'year', 'position', 'position_number', 'passphrase']
    if (len(request.GET.keys()) == len(get_keys)):
        logger.info(f"[about/views.py input_exec_info()] correct number of request.GET keys detected")

        term = 0
        year = 0
        position = 0
        position_number = 0
        for key in request.GET.keys():
            if key not in get_keys:
                logger.info(f"[about/views.py input_exec_info()] invalid key '{key}' detected")
            if key == 'term':
                term = 1
                context.update({key: request.GET[key]})
            elif key == 'year':
                year = 1
                context.update({key: request.GET[key]})
            elif key == 'position':
                position = 1
                context.update({key: request.GET[key]})
            elif key == 'position_number':
                position_number = 1
                context.update({key: request.GET[key]})
            elif key == 'passphrase':
                passphrase_number = 1
                passphrase = request.GET[key]

        if (
                (
                    (term == 0) and (year == 0) and (position == 0) and (position_number == 0) and
                    (passphrase_number == 0)
                ) or
                (
                    (term == 1) and (year == 1) and (position == 1) and (position_number == 1) and
                    (passphrase_number == 1)
                )
           ):
            logger.info(f"[about/views.py input_exec_info()] passphrase = '{passphrase}'")
            passphrase = OfficerUpdatePassphrase.objects.all().filter(
                passphrase=passphrase,
            )
            logger.info(f"[about/views.py input_exec_info()] len(passphrase) = '{len(passphrase)}'")
            if (len(passphrase) < 1):
                return HttpResponseRedirect('/about/bad_passphrase')
            logger.info(f"[about/views.py input_exec_info()] passphrase[0].used = '{passphrase[0].used}'")
            if (passphrase[0].used):
                return HttpResponseRedirect('/about/bad_passphrase')
            context.update({'tab': 'about'})
            context.update({'authenticated': request.user.is_authenticated})
            context.update({'Exec': ('Exec' in groups)})
            context.update({'ElectionOfficer': ('ElectionOfficer' in groups)}),
            context.update({'Staff': request.user.is_staff})
            context.update({'Username': request.user.username})
            context.update({'passphrase': passphrase[0].passphrase})
            logger.info(f"[about/views.py input_exec_info()] context set to '{context}'")
            logger.info(f"[about/views.py input_exec_info()] returning 'about/add_exec.html'")
            return render(request, 'about/add_exec.html', context)
        logger.info(f"[about/views.py input_exec_info()] returning '/administration/show_create_link_page'")
        return HttpResponseRedirect('/administration/show_create_link_page')
    logger.info(f"[about/views.py input_exec_info()] returning the index")
    return HttpResponseRedirect('/')


def process_exec_info(request):
    logger.info(f"[about/views.py add_exec()] request.POST={request.POST}")
    post_keys = [
        'term', 'year', 'position', 'term_position', 'name', 'sfuid', 'email',
        'gmail', 'phone_number', 'github_username', 'course1', 'course2',
        'language1', 'language2', 'bio', 'passphrase'
    ]

    if (len(request.POST.keys()) == (len(post_keys) + 1)):
        logger.info("[about/views.py add_exec()] correct number of request.POST keys detected")
        for key in request.POST.keys():
            if key not in post_keys:
                logger.info(f"[about/views.py add_exec()] invalid key '{key}' detected")
        passphrase = OfficerUpdatePassphrase.objects.all().filter(
            passphrase=request.POST['passphrase'],
        )
        if (len(passphrase) < 1):
            return HttpResponseRedirect('/about/bad_passphrase')
        if (passphrase[0].used):
            return HttpResponseRedirect('/about/bad_passphrase')
        logger.info(f"[about/views.py add_exec()] passphrase is accurate")
        passphrase = passphrase[0]
        passphrase.used = True
        passphrase.save()

        term_number = int(request.POST['year']) * 10
        if request.POST['term'] == "Spring":
            term_number = term_number + 1
        elif request.POST['term'] == "Summer":
            term_number = term_number + 2
        elif request.POST['term'] == "Fall":
            term_number = term_number + 3

        term, created = Term.objects.get_or_create(
            term=request.POST['term'],
            term_number=term_number,
            year=int(request.POST['year'])
        )
        if request.POST['phone_number'] == '':
            phone_number = 0
        else:
            phone_number = request.POST['phone_number']
        officer, created = Officer.objects.get_or_create(
            position=request.POST['position'],
            term_position_number=int(request.POST['term_position']),
            name=request.POST['name'],
            sfuid=request.POST['sfuid'],
            gmail=request.POST['gmail'],
            phone_number=int(phone_number),
            github_username=request.POST['github_username'],
            course1=request.POST['course1'],
            course2=request.POST['course2'],
            language1=request.POST['language1'],
            language2=request.POST['language2'],
            elected_term=term
        )
        post_dict = parser.parse(request.POST.urlencode())
        emails = [email.strip() for row in csv.reader(StringIO(post_dict['email']), delimiter=',') for email in row]
        for email in emails:
            AnnouncementEmailAddress.objects.get_or_create(
                email=email,
                officer=officer
            )
    return HttpResponseRedirect('/')


def bad_passphrase(request):
    groups = list(request.user.groups.values_list('name', flat=True))
    context = {
        'tab': 'about',
        'authenticated': request.user.is_authenticated,
        'Exec': ('Exec' in groups),
        'ElectionOfficer': ('ElectionOfficer' in groups),
        'Staff': request.user.is_staff,
        'Username': request.user.username
    }
    return render(request, 'about/bad_passphrase.html', context)
