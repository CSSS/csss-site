from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
# from django.core.files import File
import json
# Register your models here.
from about.models import Officer, Term, SourceFile, AnnouncementEmailAddress, EmailList
# from django import forms


def get_term(term, year, term_number):
    retrieved_objects = Term.objects.all().filter(
        term=term,
        year=year,
        term_number=term_number
    )
    if len(retrieved_objects) == 0:
        term = Term(
            term=term,
            year=year,
            term_number=term_number
        )
        term.save()
        return term
    return retrieved_objects[0]


def save_officer(term_position_number, officer_info, term_number):
    term = get_term(officer_info['term'], officer_info['year'], term_number)
    retrieved_objects = Officer.objects.all().filter(
        position=officer_info['position'],
        term_position_number=term_position_number,
        name=officer_info['name'],
        sfuid=officer_info['sfuid'],
        phone_number=officer_info['phone_number'],
        github_username=officer_info['github_username'],
        gmail=officer_info['gmail'],
        course1=officer_info['fav_course_1'],
        course2=officer_info['fav_course_2'],
        language1=officer_info['fav_language_1'],
        language2=officer_info['fav_language_2'],
        bio=officer_info['bio'],
        image=officer_info['profile_pic_path'],
        elected_term=term
    )
    if len(retrieved_objects) == 0:
        officer = Officer(
            position=officer_info['position'],
            term_position_number=term_position_number,
            name=officer_info['name'],
            sfuid=officer_info['sfuid'],
            phone_number=officer_info['phone_number'],
            github_username=officer_info['github_username'],
            gmail=officer_info['gmail'],
            course1=officer_info['fav_course_1'],
            course2=officer_info['fav_course_2'],
            language1=officer_info['fav_language_1'],
            language2=officer_info['fav_language_2'],
            bio=officer_info['bio'],
            image=officer_info['profile_pic_path'],
            elected_term=term
        )
        officer.save()
        for email in officer_info['announcement_emails']:
            email_object = AnnouncementEmailAddress(email=email, officer=officer)
            email_object.save()
    else:
        officer = retrieved_objects[0]
        for email in officer_info['announcement_emails']:
            email_object = AnnouncementEmailAddress(email=email, officer=officer)
            email_object.save()


def import_officer_for_term(file):
    position = 1
    previous_term_number = 0
    print(f"[import_officer_for_term] will now try and read file {file}")
    with open(file) as f:
        officers = json.load(f)
        for officer in officers:
            term_number = int(officer['year']) * 10
            if officer['term'] == "Spring":
                term_number = term_number + 1
            elif officer['term'] == "Summer":
                term_number = term_number + 2
            elif officer['term'] == "Fall":
                term_number = term_number + 3
            if (previous_term_number != term_number):
                position = 1
            save_officer(position, officer, term_number)
            position += 1
            previous_term_number = term_number


def import_specific_term_officers(mailbox_admin, request, queryset):
    for file in queryset.all():
        import_officer_for_term(str(file.json_file.file))


import_specific_term_officers.short_description = _('Save Officers Specified in File')


class TermAdmin(admin.ModelAdmin):
    list_display = ('term', 'year', 'term_number')


admin.site.register(Term, TermAdmin)


class OfficerAdmin(admin.ModelAdmin):
    # form = OfficerForm
    list_display = (
        'elected_term', 'term_position_number', 'position', 'name', 'sfuid', 'phone_number',
        'github_username', 'gmail', 'course1', 'course2', 'language1', 'language2'
    )


admin.site.register(Officer, OfficerAdmin)


class SourceFileAdmin(admin.ModelAdmin):
    # form = OfficerForm
    list_display = ('json_file',)

    actions = [import_specific_term_officers]


admin.site.register(SourceFile, SourceFileAdmin)


class AnnouncementEmailAdmin(admin.ModelAdmin):
    # form = OfficerForm
    list_display = ('email', 'officer', 'get_term')

    def get_term(self, obj):
        return obj.officer.elected_term
    get_term.short_description = "Elected Term"
    get_term.admin_order_field = "Elected_Term"


admin.site.register(AnnouncementEmailAddress, AnnouncementEmailAdmin)


class EmailListAdmin(admin.ModelAdmin):
    # form = OfficerForm
    list_display = ('email', 'officer', 'get_term')

    def get_term(self, obj):
        return obj.officer.elected_term
    get_term.short_description = "Elected Term"
    get_term.admin_order_field = "Elected_Term"


admin.site.register(EmailList, EmailListAdmin)
