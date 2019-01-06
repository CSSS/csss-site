from django.shortcuts import render

def index(request):
	print("Comp Sci Guide index")
	return render(request, 'comp_sci_guide/course_map.html', {'tab': 'comp_sci_guide'})

def software(request):
	print("Software index")
	return render(request, 'comp_sci_guide/software.html', {'tab': 'comp_sci_guide'})

def textbooks(request):
	print("textbook index")
	return render(request, 'comp_sci_guide/textbooks.html', {'tab': 'comp_sci_guide'})

def courseReview(request):
	print("course reviews index")
	return render(request, 'comp_sci_guide/course_reviews.html', {'tab': 'comp_sci_guide'})
# Create your views here.
