from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import NameForm

def index(request):
	print("constitution index")
	return render(request, 'documents/constitution.html')

def policies(request):
	print("policies index")
	return render(request, 'documents/policies.html')

def photos(request):
	print("photo gallery index")
  if request.method == 'POST':
    form = NameForm(request.POST)
    if form.is_valid():
      return HttpResponseRedirect('/thanks/')
  else:
    form = NameForm()

	return render(request, 'documents/photo_gallery.html', {'form': form})
# Create your views here.
