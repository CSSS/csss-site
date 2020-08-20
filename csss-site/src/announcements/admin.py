from django.contrib import admin
from announcements.models import Post, AnnouncementAttachment, Announcement, LatestAnnouncementPage

admin.site.register(Post)

admin.site.register(AnnouncementAttachment)

admin.site.register(Announcement)

admin.site.register(LatestAnnouncementPage)
