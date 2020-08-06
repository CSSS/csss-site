from django.conf.urls import url, include
from django.contrib import admin

from . import views

from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    url(r'^'+settings.URL_PATTERN+'admin/', admin.site.urls),
    url(r'^'+settings.URL_PATTERN+'about/', include('about.urls')),
    url(r'^'+settings.URL_PATTERN+'documents/', include('documents.urls')),
    url(r'^'+settings.URL_PATTERN+'events/', include('events.urls')),
    url(r'^'+settings.URL_PATTERN+'statics/', include('static_pages.urls')),
    url(r'^'+settings.URL_PATTERN+'announcements/', include('announcements.urls')),
    url(r'^'+settings.URL_PATTERN+'elections/', include('elections.urls')),
    url(r'^' + settings.URL_PATTERN + 'resource_management/', include('resource_management.urls')),
    url(r'^'+settings.URL_PATTERN+'administration/', include('administration.urls')),
    url(r'^'+settings.URL_PATTERN+'$', views.index, name="index"),
    url(r'^' + settings.URL_PATTERN + 'error/', views.errors, name="error page"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
