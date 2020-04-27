from django.conf.urls import url, include
from django.contrib import admin

from . import views

from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    url(r'^'+settings.URL_ROOT+'admin/', admin.site.urls),
    url(r'^'+settings.URL_ROOT+'about/', include('about.urls')),
    url(r'^'+settings.URL_ROOT+'documents/', include('documents.urls')),
    url(r'^'+settings.URL_ROOT+'events/', include('events.urls')),
    url(r'^'+settings.URL_ROOT+'comp_sci_guide/', include('comp_sci_guide.urls')),
    url(r'^'+settings.URL_ROOT+'bursaries_and_awards/', include('bursaries_and_awards.urls')),
    url(r'^'+settings.URL_ROOT+'announcements/', include('announcements.urls')),
    url(r'^'+settings.URL_ROOT+'elections/', include('elections.urls')),
    url(r'^'+settings.URL_ROOT+'administration/', include('administration.urls')),
    url(r'^'+settings.URL_ROOT+'$', views.index, name="index"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
