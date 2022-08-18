from django.shortcuts import render

from about.views.Constants import TAB_STRING
from csss.views.context_creation.create_main_context import create_main_context


def who_we_are(request):
    """
    Show the page what details what CSSS is about
    """
    return render(request, 'about/who_we_are.html', create_main_context(request, TAB_STRING))