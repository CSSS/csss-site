from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework import routers

from about.views.rest_framework_views.term_view_set import TermViewSet
from .views import views
from .views.crons.Constants import CRON_LOGS_BASE_URL_KEY, CRON_JOBS_BASE_URL_KEY
from .views.crons.cron import cron
from .views.crons.cron_logs import cron_logs
from .views.errors import errors
from .views.login import LoginView, LogoutView

router = routers.DefaultRouter()

router.register('terms', TermViewSet)

urlpatterns = [
    url(r'^' + settings.URL_PATTERN + 'admin/', admin.site.urls),
    url(r'^' + settings.URL_PATTERN + 'about/', include('about.urls')),
    url(r'^' + settings.URL_PATTERN + 'events/', include('events.urls')),
    url(r'^' + settings.URL_PATTERN + 'statics/', include('static_pages.urls')),
    url(r'^' + settings.URL_PATTERN + 'elections/', include('elections.urls')),
    url(r'^' + settings.URL_PATTERN + 'resource_management/', include('resource_management.urls')),
    url(r'^' + settings.URL_PATTERN + '$', views.index, name="index"),
    url(r'^' + settings.URL_PATTERN + 'markdown', views.md, name="Markdown"),
    url(r'^' + settings.URL_PATTERN + CRON_JOBS_BASE_URL_KEY + '$', cron, name="cron"),
    url(r'^' + settings.URL_PATTERN + CRON_LOGS_BASE_URL_KEY + '(?P<log_location>.+)', cron_logs, name="cron_logs"),
    url(r'^errors', errors.index, name='errors'),
    url(r'^' + settings.URL_PATTERN + 'login', LoginView.as_view(), name='login'),
    url(r'^' + settings.URL_PATTERN + 'logout', LogoutView.as_view(), name='logout'),
    url(r'^' + settings.URL_PATTERN + "api/", include((router.urls, 'api_app')))
]
if settings.ENVIRONMENT == "LOCALHOST":
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
