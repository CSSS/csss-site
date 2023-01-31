from django.contrib import admin

from announcements.models import ManualAnnouncement, Announcement


class ManualAnnouncementAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'date')


admin.site.register(ManualAnnouncement, ManualAnnouncementAdmin)


class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('id', 'term', 'date', 'author', 'display', 'email', 'manual_announcement')


admin.site.register(Announcement, AnnouncementAdmin)
