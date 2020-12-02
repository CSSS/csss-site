from django.contrib import admin

# Register your models here.
from resource_management.models import ProcessNewOfficer, NonOfficerGoogleDriveUser, GoogleDrivePublicFile, \
    NonOfficerGithubMember, \
    NaughtyOfficer, OfficerGithubTeamMapping, OfficerGithubTeam, GoogleMailAccountCredentials


class ProcessNewOfficerAdmin(admin.ModelAdmin):
    # form = OfficerForm
    list_display = (
        'passphrase', 'start_date', 'new_start_date', 'term', 'year', 'position_name', 'used',
        'position_index', 'used'
    )


admin.site.register(ProcessNewOfficer, ProcessNewOfficerAdmin)


class GoogleMailAccountCredentialsAdmin(admin.ModelAdmin):
    list_display = ('username', 'password')


admin.site.register(GoogleMailAccountCredentials, GoogleMailAccountCredentialsAdmin)


class NonOfficerGoogleDriveUserAdmin(admin.ModelAdmin):
    # form = OfficerForm
    list_display = ('gmail', 'name', 'file_id', 'file_name')


admin.site.register(NonOfficerGoogleDriveUser, NonOfficerGoogleDriveUserAdmin)


class GoogleDrivePublicFileAdmin(admin.ModelAdmin):
    # form = OfficerForm
    list_display = ('file_id', 'link', 'file_name')


admin.site.register(GoogleDrivePublicFile, GoogleDrivePublicFileAdmin)


class OfficerGithubTeamMappingAdmin(admin.ModelAdmin):
    list_display = ('position_name', 'team_name')


admin.site.register(OfficerGithubTeamMapping, OfficerGithubTeamMappingAdmin)


class OfficerGithubTeamAdmin(admin.ModelAdmin):
    list_display = ('team_name', 'officer')


admin.site.register(OfficerGithubTeam, OfficerGithubTeamAdmin)


class NonOfficerGithubMemberAdmin(admin.ModelAdmin):
    # form = OfficerForm
    list_display = ('legal_name', 'username', 'team_name')


admin.site.register(NonOfficerGithubMember, NonOfficerGithubMemberAdmin)


class NaughtyOfficerAdmin(admin.ModelAdmin):
    list_display = ('name',)


admin.site.register(NaughtyOfficer, NaughtyOfficerAdmin)
