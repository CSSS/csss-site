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


class OfficerEmailListAndPositionMappingAdmin(admin.ModelAdmin):
    list_display = (
        'position_index', 'position_name', 'email', 'github', 'google_drive', 'marked_for_deletion',
        'elected_via_election_officer', 'starting_month', 'number_of_terms', 'executive_officer'
    )


admin.site.register(OfficerEmailListAndPositionMapping, OfficerEmailListAndPositionMappingAdmin)
