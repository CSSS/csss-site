from django.conf.urls import url

from . import views


urlpatterns = (
    url(r'^success$', views.success, name='success'),
    url(r'^multiple$', views.SubmissionUploadPage.as_view(), name='multiple_example')
)
