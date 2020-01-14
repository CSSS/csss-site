from django.contrib import admin
from announcements.models import Post, AnnouncementAttachment
# Register your models here.

admin.site.register(Post)

admin.site.register(AnnouncementAttachment)
