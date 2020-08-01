from django.shortcuts import render

from csss.views_helper import create_main_context


def index(request):
    return render(request, 'bursaries_and_awards/index.html', create_main_context(request, 'bursaries_and_awards'))
