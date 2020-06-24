from django.contrib import admin

# Register your models here.
from administration.models import ProcessNewOfficer, GDriveUser, GDrivePublicFile, NonOfficerGithubMember, \
    NaughtyOfficer


class NaughtyOfficerAdmin(admin.ModelAdmin):
    list_display = ('name',)


admin.site.register(NaughtyOfficer, NaughtyOfficerAdmin)


class ProcessNewOfficerAdmin(admin.ModelAdmin):
    # form = OfficerForm
    list_display = ('passphrase', 'used')


admin.site.register(ProcessNewOfficer, ProcessNewOfficerAdmin)


class GDriveUserAdmin(admin.ModelAdmin):
    # form = OfficerForm
    list_display = ('gmail', 'name', 'file_id')


admin.site.register(GDriveUser, GDriveUserAdmin)


class GDrivePublicFileAdmin(admin.ModelAdmin):
    # form = OfficerForm
    list_display = ('file_id', 'link')


admin.site.register(GDrivePublicFile, GDrivePublicFileAdmin)


class NonOfficerGithubMemberAdmin(admin.ModelAdmin):
    # form = OfficerForm
    list_display = ('legal_name', 'username', 'team_name')


admin.site.register(NonOfficerGithubMember, NonOfficerGithubMemberAdmin)
