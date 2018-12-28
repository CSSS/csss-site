from django.shortcuts import render

# Create your views here.
from django.views import generic

from .models import NominationPage, Nominee
from datetime import datetime 

class NomineeDetailView(generic.DetailView):
	model = Nominee

class NomineeListView(generic.ListView):
	def get_queryset(self):
		page = NominationPage.objects.get(slug=self.kwargs['slug'])
		if page.datePublic <= (datetime.now()):	
			return Nominee.objects.filter(nominationPage__slug = self.kwargs['slug']).all().order_by('Position')
		else:
			return Nominee.objects.filter(nominationPage__slug = 'None')