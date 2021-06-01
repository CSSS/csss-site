from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^regular_events$', views.regular_events, name='gm'),
    url(r'^frosh/', include('events.frosh.urls')),
    url(r'^mm/', include('events.mountain_madness.urls')),
    url(r'^fall_hacks/', include('events.fall_hacks.urls'))
]
