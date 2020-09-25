from django.contrib import admin
from django_markdown.admin import MarkdownModelAdmin

from announcements.models import ManualAnnouncement, Announcement


class ManualAnnouncementAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'date')


admin.site.register(ManualAnnouncement, MarkdownModelAdmin)


class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('id', 'term', 'email', 'post', 'date', 'author', 'display')


admin.site.register(Announcement, AnnouncementAdmin)
