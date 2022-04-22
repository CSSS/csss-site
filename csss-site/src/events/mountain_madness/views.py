from django.shortcuts import render

from csss.views.context_creation.create_main_context import create_main_context

TAB = 'events'


def mm2021_submissions(request):
    return render(request,
                  'mountain_madness/2021/mountain_madness2021_submissions.html', create_main_context(request, TAB))

def mm2022(request):
    return render(request, 'mountain_madness/2022/mountain_madness2022.html', create_main_context(request, TAB))

def mm2021(request):
    return render(request, 'mountain_madness/2021/mountain_madness2021.html', create_main_context(request, TAB))


def mm2020(request):
    return render(request, 'mountain_madness/2020/mountain_madness2020.html', create_main_context(request, TAB))


def mm2019(request):
    return render(request, 'mountain_madness/2019/mountain_madness2019.html', create_main_context(request, TAB))
