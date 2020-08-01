from django.conf.urls import url

from .views import views
from .views.frosh import frosh2012, frosh2013, frosh2014, frosh2015

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
    url(r'^frosh/2014$', frosh2014.index, name="Frosh Week 2014"),
    url(r'^frosh/2014/schedule$', frosh2014.schedule, name="Frosh Week 2014 Schedule"),
    url(r'^frosh/2014/registration$', frosh2014.registration, name="Frosh Week 2014 Registration"),
    url(r'^frosh/2014/faq$', frosh2014.faq, name="Frosh Week 2014 F.A.Q."),
    url(r'^frosh/2014/sponsors$', frosh2014.sponsors, name="Frosh Week 2014 Sponsors"),
    url(r'^frosh/2014/contact$', frosh2014.contact, name="Frosh Week 2014 Contact"),
    url(r'^frosh/2015$', frosh2015.index, name="Frosh Week 2015"),
    url(r'^frosh/2015/frosh$', frosh2015.frosh, name="Frosh Week 2015 Frosh"),
    url(r'^frosh/2015/conditions$', frosh2015.conditions, name="Frosh Week 2015 Conditions"),
    url(r'^frosh/2015/contact$', frosh2015.contact, name="Frosh Week 2015 Contact Us"),
    url(r'^$', views.index, name='index'),
]
