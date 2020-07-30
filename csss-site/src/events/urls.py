from django.conf.urls import url

from .views import views
from .views.frosh import frosh2012, frosh2013

urlpatterns = [
    url(r'^general_meetings$', views.gm, name='gm'),
    url(r'^board_games$', views.board_games, name='board_games'),
    url(r'^mountain_madness2020$', views.mountain_madness2020,name='mountain_madness2020'),
    url(r'^frosh/$', views.frosh_week, name="Frosh Week"),
    url(r'^frosh/2012$', frosh2012.index, name="Frosh Week 2012"),
    url(r'^frosh/2012/schedule$', frosh2012.schedule, name="Frosh Week 2012 Schedule"),
    url(r'^frosh/2012/registration$', frosh2012.registration, name="Frosh Week 2012 Registration"),
    url(r'^frosh/2012/faq$', frosh2012.faq, name="Frosh Week 2012 F.A.Q."),
    url(r'^frosh/2012/contact$', frosh2012.contact, name="Frosh Week 2012 Contact"),
    url(r'^frosh/2012/sponsors$', frosh2012.sponsors, name="Frosh Week 2012 Sponsors"),
    url(r'^frosh/2013$', frosh2013.index, name="Frosh Week 2013"),
    url(r'^frosh/2013/schedule$', frosh2013.schedule, name="Frosh Week 2013 Schedule"),
    url(r'^frosh/2013/registration$', frosh2013.registration, name="Frosh Week 2013 Registration"),
    url(r'^frosh/2013/faq$', frosh2013.faq, name="Frosh Week 2013 F.A.Q."),
    url(r'^frosh/2013/sponsors$', frosh2013.sponsors, name="Frosh Week 2013 Sponsors"),
    url(r'^frosh/2013/contact$', frosh2013.contact, name="Frosh Week 2013 Contact"),
    url(r'^$', views.index, name='index'),
]
