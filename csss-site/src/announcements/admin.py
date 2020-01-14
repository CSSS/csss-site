from django.contrib import admin
from announcements.models import Post, AnnouncementAttachment

admin.site.register(Post)

admin.site.register(AnnouncementAttachment)
