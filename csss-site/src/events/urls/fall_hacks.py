from django.conf.urls import url


from ..views import fall_hacks

urlpatterns = [
    url(r'^fall_hacks2020$', fall_hacks.fall_hacks2020, name='fall_hacks2020'),
    url(r'^fall_hacks_submissions2020$', fall_hacks.fall_hacks_submissions2020, name='fall_hacks_submissions2020'),
]