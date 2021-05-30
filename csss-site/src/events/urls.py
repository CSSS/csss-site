from django.conf.urls import url

from .urls.fall_hacks import urlpatterns as fall_hacks_urlpatterns
from .urls.mm import urlpatterns as mm_urlpatterns
from .urls.frosh import urlpatterns as frosh_urlpatterns
from .views import views

urlpatterns = [
    url(r'^regular_events$', views.regular_events, name='gm'),
]

urlpatterns.extend(mm_urlpatterns)
urlpatterns.extend(fall_hacks_urlpatterns)
urlpatterns.extend(frosh_urlpatterns)
