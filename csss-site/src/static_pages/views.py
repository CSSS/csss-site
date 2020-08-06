from django.shortcuts import render

# Create your views here.
from csss.views_helper import create_main_context

TAB = 'more'


def bursaries(request):
    return render(request, 'static_pages/bursaries.html', create_main_context(request, TAB))


def guide(request):
    return render(request, 'static_pages/guide.html', create_main_context(request, TAB))
