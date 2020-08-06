from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^bursaries$', views.bursaries, name='gm'),
    url(r'^guide$', views.guide, name='board_games'),
]
