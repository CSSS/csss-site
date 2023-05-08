from django.contrib import admin

from csss.models import CSSSError


class CSSSErrorAdmin(admin.ModelAdmin):
    list_display = ('filename', 'message', 'processed')


admin.site.register(CSSSError, CSSSErrorAdmin)
