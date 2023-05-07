from django.shortcuts import render

from about.views.Constants import TAB_STRING
from csss.views.context_creation.create_main_context import create_main_context

def sample_tool(request):
    return render(request, 'sample_tool.html', create_main_context(request, "more"))
