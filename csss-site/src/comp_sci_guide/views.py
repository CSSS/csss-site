from django.shortcuts import render

from csss.views_helper import create_main_context


def software(request):
    return render(request, 'comp_sci_guide/software.html', create_main_context(request, "comp_sci_guide"))
