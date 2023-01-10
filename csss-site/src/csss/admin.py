from django.contrib import admin

from csss.models import Error


class ErrorAdmin(admin.ModelAdmin):
    list_display = ('level', 'filename', 'message', 'processed')


admin.site.register(Error, ErrorAdmin)
