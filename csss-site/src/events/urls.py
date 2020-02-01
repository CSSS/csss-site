from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^general_meetings$', views.gm, name='gm'),
    url(r'^board_games$', views.board_games, name='board_games'),
    url(r'^game_jam$', views.game_jam, name='game_jam'),
    url(r'^frosh_week$', views.frosh_week, name='froshWeek'),
    url(r'^mountain_madness2020$', views.mountain_madness2020,
        name='mountain_madness2020'),
    url(r'^$', views.index, name='index'),
]
