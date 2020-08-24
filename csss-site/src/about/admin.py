from django.contrib import admin

# Register your models here.
from about.models import Officer, Term, AnnouncementEmailAddress


class TermAdmin(admin.ModelAdmin):
    list_display = ('term', 'year', 'term_number')


admin.site.register(Term, TermAdmin)


class OfficerAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'elected_term', 'term_position_number', 'position', 'sfuid', 'phone_number',
        'github_username', 'gmail', 'course1', 'course2', 'language1', 'language2'
    )


admin.site.register(Officer, OfficerAdmin)


class AnnouncementEmailAdmin(admin.ModelAdmin):
    list_display = ('officer', 'email')


admin.site.register(AnnouncementEmailAddress, AnnouncementEmailAdmin)
