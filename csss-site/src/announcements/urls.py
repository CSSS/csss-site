from django.conf.urls import url
from django.views.generic import ListView, DetailView
from announcements.models import Post

urlpatterns = [
    url(r'^(?P<pk>\d+)$', DetailView.as_view(model=Post, template_name='announcements/post.html')),
    url(
        r'^$',
        ListView.as_view(
            queryset=Post.objects.all().order_by("date")[:25],
            template_name="announcements/announcements.html"
        )
    )
]
