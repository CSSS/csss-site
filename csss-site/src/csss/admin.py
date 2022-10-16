from django.contrib import admin

from csss.models import CronJob


class CronJobAdmin(admin.ModelAdmin):
    list_display = ('job_name', 'schedule')


admin.site.register(CronJob, CronJobAdmin)
