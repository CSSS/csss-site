from django.shortcuts import render

from administration.views.views_helper import create_context


def index(request):
    return render(
        request,
        'bursaries_and_awards/index.html',
        create_context(
            request,
            'bursaries_and_awards'
        )
    )
