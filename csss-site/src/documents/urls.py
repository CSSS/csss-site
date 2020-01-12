from django.conf.urls import url, include
# from django.contrib import admin

from . import views

urlpatterns = [
    url(r'^policies$', views.policies, name='policies'),
    url(r'^photo_gallery$', views.events, name='events'),
    url(r'^photo_gallery/', views.album, name='album'),
    url(r'^upload/', include('django_file_form.urls')),
    url(r'^file_uploading/', include('file_uploads.urls')),  # the one that does the redirect
    url(r'^$', views.index, name='index'),
]
