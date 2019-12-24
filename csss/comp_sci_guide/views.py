from django.shortcuts import render

def index(request):
    print("Comp Sci Guide index")
    context = {
        'tab': 'comp_sci_guide',
        'authenticated' : request.user.is_authenticated,
    }
    return render(request, 'comp_sci_guide/course_map.html', context)

def software(request):
    print("Software index")
    context = {
        'tab': 'comp_sci_guide',
        'authenticated' : request.user.is_authenticated,
    }
    return render(request, 'comp_sci_guide/software.html', context)

def textbooks(request):
    print("textbook index")
    context = {
        'tab': 'comp_sci_guide',
        'authenticated' : request.user.is_authenticated,
    }
    return render(request, 'comp_sci_guide/textbooks.html', context)

def courseReview(request):
    print("course reviews index")
    context = {
        'tab': 'comp_sci_guide',
        'authenticated' : request.user.is_authenticated,
    }
    return render(request, 'comp_sci_guide/course_reviews.html', context)
# Create your views here.
