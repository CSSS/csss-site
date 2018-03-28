"""csss URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from . import views

urlpatterns = [
  url(r'^list_of_officers/fall_2017$', views.fall_2017, name='fall_2017'),
  url(r'^list_of_officers/spring_2018$', views.spring_2018, name='spring_2018'),
  url(r'^list_of_officers/summer_2017$', views.summer_2017, name='summer_2017'),
  url(r'^list_of_officers/spring_2017$', views.spring_2017, name='spring_2017'),
	url(r'^list_of_officers$',views.listOfOfficers, name='listOfOfficers'),
	url(r'^who_we_are$', views.index, name='index'),
]
