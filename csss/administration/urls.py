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
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views

from . import views
# from django.conf.urls.static import static
# from django.conf import settings

urlpatterns = [
        url(r'^admin$', admin.site.urls),
        
        url(r'^login$', views.login, name='login'),
	url(r'^logout$', views.logout, name='logout'),
        url(r'^exec$', views.exec, name='exec'),
	url(r'^elections/select_election$', views.select_election, name='select_election'),
	url(r'^elections/determine_election_action$', views.determine_election_action, name='determine_election_action'),
	url(r'^elections/modify_election$', views.modify_election, name='modify_election'),
	url(r'^elections/create$', views.create_election, name='create_election'),
	url(r'^elections$', views.elections, name='elections'),
        url(r'^merch$', views.merch, name='merch'),
	url(r'^post$', views.post, name='post'),
        url(r'^fileUpload$', views.fileUpload, name='file upload'),
]
