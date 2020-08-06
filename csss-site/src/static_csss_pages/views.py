from django.shortcuts import render

# Create your views here.
from csss.views_helper import create_main_context

TAB_STRING = 'more'


def bursaries(request):
    return render(request, 'static_csss_pages/bursaries_and_awards.html', create_main_context(request, TAB_STRING))


def guide(request):
    return render(request, 'static_csss_pages/comp_sci_guide.html', create_main_context(request, TAB_STRING))
