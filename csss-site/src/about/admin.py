from django.contrib import admin

# Register your models here.
from about.models import Officer, Term, AnnouncementEmailAddress, OfficerEmailListAndPositionMapping


class TermAdmin(admin.ModelAdmin):
    list_display = ('term', 'year', 'term_number')


admin.site.register(Term, TermAdmin)


class OfficerAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'elected_term', 'position_index', 'position_name', 'start_date',
        'sfuid', 'sfu_email_alias', 'phone_number', 'github_username', 'gmail',
        'course1', 'course2', 'language1', 'language2'
    )


admin.site.register(Officer, OfficerAdmin)


class AnnouncementEmailAdmin(admin.ModelAdmin):
    list_display = ('officer', 'email')


admin.site.register(AnnouncementEmailAddress, AnnouncementEmailAdmin)


class OfficerPositionMappingAdmin(admin.ModelAdmin):
    list_display = ('position_name', 'email', 'position_index', 'marked_for_deletion')


admin.site.register(OfficerEmailListAndPositionMapping, OfficerPositionMappingAdmin)
