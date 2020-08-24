from django.conf.urls import url

from .views import views, manage_officers

urlpatterns = [
    url(r'^list_of_officers$', views.list_of_officers, name='list_of_officers'),
    url(r'^who_we_are$', views.index, name='index'),

    url(r'^show_create_link_page$', manage_officers.show_create_link_page, name='Create Link'),
    url(r'^show_page_with_creation_links$', manage_officers.show_page_with_creation_links, name="Show Links"),
    url(r'^allow_officer_to_choose_name$', manage_officers.allow_officer_to_choose_name, name='Add an Officer'),
    url(r'^display_page_for_officer_to_input_info$', manage_officers.display_page_for_officers_to_input_their_info,
        name='Add an Officer'),
    url(r'^input_officer_info$', manage_officers.process_information_entered_by_officer, name='Add an Officer')
]
