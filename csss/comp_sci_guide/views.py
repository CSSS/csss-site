from django.shortcuts import render

def index(request):
	print("Comp Sci Guide index")
	return render(request, 'comp_sci_guide/course_map.html')

def software(request):
	print("Software index")
	return render(request, 'comp_sci_guide/software.html')

def textbooks(request):
	print("textbook index")
	return render(request, 'comp_sci_guide/textbooks.html')

def course_reviews(request):
	print("course reviews index")
	return render(request, 'comp_sci_guide/course_reviews.html')
# Create your views here.
