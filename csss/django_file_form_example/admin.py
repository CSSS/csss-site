from django.contrib import admin

# Register your models here.

from .models import Example, Event_Uploads, Event_File


class Event_FileInline(admin.TabularInline):
    model = Event_File


class Event_UploadsAdmin(admin.ModelAdmin):
    inlines = [Event_FileInline]


#admin.site.register(Example)
admin.site.register(Event_Uploads, Event_UploadsAdmin)
