from django.conf.urls import url
from . import views, officer_management


urlpatterns = [
    url(r'^login$', views.login, name='login'),
    url(r'^logout$', views.logout, name='logout'),
    url(r'^officer/show_create_link_page$', officer_management.show_create_link_page, name='Create Link'),
    url(r'^officer/create_link$', officer_management.create_link, name='Create Link'),
    url(
        r'^officer/create_or_update_json$',
        officer_management.create_or_update_specified_term_with_provided_json,
        name='Create Link'
    )
]
