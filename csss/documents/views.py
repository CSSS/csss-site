from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from documents.models import Media, Event, Album

def index(request):
	print("constitution index")
	return render(request, 'documents/constitution.html', {'tab': 'documents'})

def policies(request):
	print("policies index")
	return render(request, 'documents/policies.html', {'tab': 'documents'})


def photo_gallery(request):
	print("photo_gallery")
	events = Event.objects.all().filter()
	albums = Album.objects.all().filter()


	return render(request, 'documents/photo_gallery.html', {'events': events, 'albums': albums, 'tab': 'documents'})
