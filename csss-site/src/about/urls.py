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
from django.conf.urls import url  # , include
# from django.contrib import admin

from . import views

urlpatterns = [
    url(r'^list_of_officers$', views.list_of_officers, name='list_of_officers'),
    url(r'^input_exec_info$', views.input_exec_info, name='Add an Exec'),
    url(r'^process_exec_info$', views.process_exec_info, name='Add an Exec'),
    url(r'^who_we_are$', views.index, name='index'),
    url(r'^bad_passphrase$', views.bad_passphrase, name='index'),
]
