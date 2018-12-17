from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView

def index(request):
	print("constitution index")
	return render(request, 'documents/constitution.html')

def policies(request):
	print("policies index")
	return render(request, 'documents/policies.html')


def photo_gallery(request):
	if request.method == 'POST':
		form = ContactForm(request.POST)
		title = form['title']
		#additional_info = form.cleaned_data['additional_info']
		additional_info = form['additional_info']
		#contact_info = form.cleaned_data['contact_info']
		contact_info = form['contact_info']
		#photos = request.FILES.getlist('pics_from_event')
		photos = request.FILES.getlist('pics_from_event')
		if photos is not None:
			print("photos type=["+str(type(photos))+"]")
			for photo in photos:
				print("photo=["+str(photo)+"]")
		else:
			print("no pictures detected")
	else:
		form = ContactForm()
		args = {'form': form}
		print("photo_gallery not POST")
		return render(request, 'documents/photo_gallery.html', args)

def photos(request):
	print("photo gallery index")
	return render(request, 'documents/photo_gallery.html')