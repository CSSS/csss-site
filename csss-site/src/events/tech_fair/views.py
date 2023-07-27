from django.shortcuts import render

from csss.views.context_creation.create_main_context import create_main_context

TAB = 'events'


def tech_fair2022(request):
    return render(request, 'tech_fair/2022/tech_fair.html', create_main_context(request, TAB))


def tech_fair2022_main(request):
    return render(request, 'tech_fair/2022/tech_fair_main.html', create_main_context(request, TAB))


def tech_fair_2023(request):
    return render(request, 'tech_fair/2023/tech_fair.html', create_main_context(request, TAB))


def tech_fair_2023_company_package(request):
    return render(request, 'tech_fair/2023/tech_fair_company_package.html', create_main_context(request, TAB))
