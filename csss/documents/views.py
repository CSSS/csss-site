from django.shortcuts import render

def index(request):
	print("constitution index")
	return render(request, 'documents/constitution.html')

def bylaws(request):
	print("bylaws index")
	return render(request, 'documents/bylaws.html')

def sfss(request):
	print("sfss documents index")
	return render(request, 'documents/sfss_documents.html')

def photos(request):
	print("photo gallery index")
	return render(request, 'documents/photo_gallery.html')
# Create your views here.
