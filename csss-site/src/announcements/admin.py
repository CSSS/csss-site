from django.contrib import admin
from announcements.models import Post, PostsAndEmails

admin.site.register(Post)

admin.site.register(PostsAndEmails)
