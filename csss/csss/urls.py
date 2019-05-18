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

from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
	url(r'^admin/', admin.site.urls),
	url(r'^blog/', include('blog.urls')),
	url(r'^about/',include('about.urls')),
	url(r'^documents/', include('documents.urls')),
    url(r'^events/', include('events.urls')),
    url(r'^750_project/', include('750_project.urls')),
    url(r'^comp_sci_guide/', include('comp_sci_guide.urls')),
    url(r'^bursaries_and_awards/', include('bursaries_and_awards.urls')),
    url(r'^announcements/', include('announcements.urls')),
    url(r'^elections/', include('elections.urls')),
    url(r'^$', views.index, name="index"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
