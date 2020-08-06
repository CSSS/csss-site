from django.shortcuts import render

from csss.views_helper import create_main_context

TAB_STRING = 'more'


def bursaries(request):
    return render(request, 'static_pages/bursaries_and_awards.html', create_main_context(request, TAB_STRING))


def guide(request):
    return render(request, 'static_pages/comp_sci_guide.html', create_main_context(request, TAB_STRING))
