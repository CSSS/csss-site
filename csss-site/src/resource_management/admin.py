from django.contrib import admin

# Register your models here.
from resource_management.models import ProcessNewOfficer, NonOfficerGoogleDriveUser, GoogleDrivePublicFile, \
    NonOfficerGithubMember, \
    OfficerPositionGithubTeam, OfficerPositionGithubTeamMapping


class ProcessNewOfficerAdmin(admin.ModelAdmin):
    list_display = (
        'passphrase', 'start_date', 'use_new_start_date', 'term', 'year', 'position_name', 'used',
        'position_index'
    )


admin.site.register(ProcessNewOfficer, ProcessNewOfficerAdmin)


class NonOfficerGoogleDriveUserAdmin(admin.ModelAdmin):
    list_display = ('gmail', 'name', 'file_id', 'file_name')


admin.site.register(NonOfficerGoogleDriveUser, NonOfficerGoogleDriveUserAdmin)


class GoogleDrivePublicFileAdmin(admin.ModelAdmin):
    list_display = ('file_id', 'link', 'file_name')


admin.site.register(GoogleDrivePublicFile, GoogleDrivePublicFileAdmin)


class OfficerPositionGithubTeamAdmin(admin.ModelAdmin):
    list_display = ('team_name', 'marked_for_deletion')


admin.site.register(OfficerPositionGithubTeam, OfficerPositionGithubTeamAdmin)


class OfficerPositionGithubTeamMappingAdmin(admin.ModelAdmin):
    list_display = ('github_team', 'officer_position_mapping')


admin.site.register(OfficerPositionGithubTeamMapping, OfficerPositionGithubTeamMappingAdmin)


class NonOfficerGithubMemberAdmin(admin.ModelAdmin):
    list_display = ('legal_name', 'username', 'team_name')


admin.site.register(NonOfficerGithubMember, NonOfficerGithubMemberAdmin)
