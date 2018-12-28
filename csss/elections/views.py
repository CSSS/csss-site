from django.shortcuts import render

# Create your views here.
from django.views import generic

from .models import NominationPage, Nominee
from datetime import datetime 

class NomineeDetailView(generic.DetailView):
	model = Nominee

class NomineeListView(generic.ListView):
	def get_queryset(self):
		for page in NominationPage.objects.all():
			if self.kwargs['slug'] == page.slug:
				if page.datePublic <= (datetime.now()):	
					nominee =  Nominee.objects.filter(nominationPage__slug = self.kwargs['slug'])
					print ("nominee="+str(nominee))
					nominee = nominee.all().order_by('Position')
					return nominee
				else:
					return Nominee.objects.filter(nominationPage__slug = 'None')
