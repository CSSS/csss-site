from django.shortcuts import render

from administration.views.views_helper import create_context


def software(request):
    return render(
        request,
        'comp_sci_guide/software.html',
        create_context(
            request,
            'bursaries_and_awards'
        )
    )