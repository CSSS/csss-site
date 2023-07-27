from django.conf.urls import url

from events.tech_fair import views

urlpatterns = [
    url(r'^2022$', views.tech_fair2022, name='tech_fair2022'),
    url(r'^2022/main$', views.tech_fair2022_main, name='tech_fair2022_main'),
    url(r'^2023$', views.tech_fair_2023, name='tech_fair_2023'),
    url(r'^2023/company_package$', views.tech_fair_2023_company_package, name='tech_fair_2023_pkg'),
]
