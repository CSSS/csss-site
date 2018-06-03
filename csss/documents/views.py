from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from documents.forms import ContactForm
from django.views.generic import TemplateView

def index(request):
	print("constitution index")
	return render(request, 'documents/constitution.html')

def policies(request):
	print("policies index")
	return render(request, 'documents/policies.html')


def photo_gallery(request):
  if request.method == 'POST':
    print("photo_gallery POST")
    form = ContactForm(request.POST)
    print("[photo_gallery] 1")
    print("[photo_gallery] 2")
    #form.save()
    print("form saved")
    print("[photo_gallery] 3")
    title = form['title']
    print("[photo_gallery] 4")
    print("title=["+str(title)+"]")
    print("[photo_gallery] 5")
    #additional_info = form.cleaned_data['additional_info']
    additional_info = form['additional_info']
    print("additional_info=["+str(additional_info)+"]")
    print("[photo_gallery] 6")
    #contact_info = form.cleaned_data['contact_info']
    contact_info = form['contact_info']
    print("contact_info=["+str(contact_info)+"]")
    print("[photo_gallery] 7")
    print("[photo_gallery] 8")
    #photos = request.FILES.getlist('pics_from_event')
    photos = request.FILES.getlist('pics_from_event')
    print("[photo_gallery] 9")
    if photos is not None:
      print("[photo_gallery] 10")
      print("pictures detected")
      print("[photo_gallery] 11")
      print("photos type=["+str(type(photos))+"]")
      print("[photo_gallery] 12")
      for photo in photos:
        print("[photo_gallery] 13")
        print("photo=["+str(photo)+"]")
        print("[photo_gallery] 14")
    else:
      print("[photo_gallery] 15")
      print("no pictures detected")
      print("[photo_gallery] 16")
  else:
    form = ContactForm()
    args = {'form': form}
    print("photo_gallery not POST")
    return render(request, 'documents/photo_gallery.html', args)

def photos(request):
	print("photo gallery index")
	return render(request, 'documents/photo_gallery.html')
# Create your views here.
