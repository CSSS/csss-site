from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^sample_tool/$', views.sample_tool),
    url(r'^generate_cheque_req/$', views.generate_cheque_req_tool),
    url(r'^generate_cheque_req/process/$', views.generate_cheque_req_process, name="gen_cheque_req_process")
]
