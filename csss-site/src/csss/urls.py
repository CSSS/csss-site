from django.conf.urls import url, include
from django.contrib import admin

from . import views

from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^about/', include('about.urls')),
    url(r'^documents/', include('documents.urls')),
    url(r'^events/', include('events.urls')),
    url(r'^comp_sci_guide/', include('comp_sci_guide.urls')),
    url(r'^bursaries_and_awards/', include('bursaries_and_awards.urls')),
    url(r'^announcements/', include('announcements.urls')),
    url(r'^elections/', include('elections.urls')),
    url(r'^administration/', include('administration.urls')),
    url(r'^$', views.index, name="index"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
