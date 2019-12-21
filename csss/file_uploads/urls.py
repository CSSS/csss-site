from django.conf.urls import url

from . import views


urlpatterns = (
    url(r'^success$', views.SubmissionUpoadSuccess.as_view(), name='example_success'),
    url(r'^multiple$', views.SubmissionUploadPage.as_view(), name='multiple_example')
)
