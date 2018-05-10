from django.contrib import admin
from announcements.models import Post
# Register your models here.

admin.site.register(Post)

admin.site.register(AnnouncementAttachment)