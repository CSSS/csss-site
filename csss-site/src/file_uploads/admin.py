from django.contrib import admin

from .models import UploadedFile,  UserSubmission


class ExampleFileInline(admin.TabularInline):
    model = UploadedFile


class UserSubmissionAdmin(admin.ModelAdmin):
    inlines = [ExampleFileInline]


admin.site.register(UserSubmission, UserSubmissionAdmin)
