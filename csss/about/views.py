from django.shortcuts import render
from about.models import Term, Officer, AnnouncementEmailAddress

# Create your views here.
from querystring_parser import parser
import datetime
from django.http import HttpResponseRedirect
from io import StringIO
import csv



def index(request):
    print("who we are index")
    context = {
        'tab': 'about',
        'authenticated' : request.user.is_authenticated,
    }
    return render(request, 'about/who_we_are.html', context)

def listOfOfficers(request):
    print("list of officers index")
    officers = Officer.objects.all().filter()
    now = datetime.datetime.now()
    termActive = (now.year*10) + int(now.month / 4)
    context = {
        'tab': 'about',
        'authenticated' : request.user.is_authenticated,
        'officers': officers,
        'termActive' : termActive,
    }
    return render(request, 'about/list_of_officers.html', context)

def input_exec_info(request):
    print(f"request.GET={request.GET}")
    context = {}
    get_keys = ['term', 'year', 'position', 'position_number']
    if (len(request.GET.keys()) == len(get_keys)):
        print("correct number of request.GET keys detected")

        term = 0 ; year = 0 ; position = 0 ; position_number = 0
        for key in request.GET.keys():
            if key not in get_keys:
                print(f"invalid key detected")
            if key == 'term':
                term=1
                context.update({ key : request.GET[key] })
            elif key == 'year':
                year=1
                context.update({ key : request.GET[key]})
            elif key == 'position':
                position=1
                context.update({ key : request.GET[key]})
            elif key == 'position_number':
                position_number = 1
                context.update({ key : request.GET[key]})

        if ( (term == 0) and ( year == 0) and (position == 0) and (position_number == 0) ) or \
            ( (term == 1) and (year == 1) and (position == 1) and (position_number == 1) ):
            context.update({'tab': 'about'})
            context.update({'authenticated': request.user.is_authenticated})
            print(f"context={context}")
            return render(request, 'about/add_exec.html', context)
        return HttpResponseRedirect('/administration/show_create_link_page')
    return HttpResponseRedirect('/')

def process_exec_info(request):
    print("add_exec")
    print(f"request.POST={request.POST}")
    context = {}
    post_keys = ['term', 'year', 'position', 'term_position', 'name', 'sfuid', 'email', 'gmail', 'phone_number', 'github_username', 'course1', 'course2', 'language1', 'language2', 'bio']

    if (len(request.POST.keys()) == (len(post_keys) + 1 ) ):
        print("correct number of request.POST keys detected")
        for key in request.POST.keys():
            if key not in post_keys:
                print(f"invalid key '{key}' detected")

        term_number = int(request.POST['year']) * 10
        if request.POST['term'] == "Spring":
            term_number = term_number + 1
        elif request.POST['term'] == "Summer":
            term_number = term_number + 2
        elif request.POST['term'] == "Fall":
            term_number = term_number + 3

        term, created = Term.objects.get_or_create(
            term = request.POST['term'],
            term_number = term_number ,
            year =  int(request.POST['year'])
        )
        if request.POST['phone_number'] == '':
            phone_number = 0
        else:
            phone_number = request.POST['phone_number']
        officer, created = Officer.objects.get_or_create(
            position = request.POST['position'],
            term_position_number = int(request.POST['term_position']),
            name = request.POST['name'],
            sfuid = request.POST['sfuid'],
            gmail = request.POST['gmail'],
            phone_number = int(phone_number),
            github_username = request.POST['github_username'],
            course1 = request.POST['course1'],
            course2 = request.POST['course2'],
            language1 = request.POST['language1'],
            language2 = request.POST['language2'],
            elected_term = term
        )
        post_dict = parser.parse(request.POST.urlencode())
        emails = [email.strip() for row in csv.reader(StringIO(post_dict['email']), delimiter=',') for email in row]
        for email in emails:
            AnnouncementEmailAddress.objects.get_or_create(
                email = email,
                officer = officer
            )
    return HttpResponseRedirect('/')
