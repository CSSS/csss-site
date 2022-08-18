from django.contrib import admin

# Register your models here.
from resource_management.models import NonOfficerGoogleDriveUser, GoogleDrivePublicFile, \
    NonOfficerGithubMember, \
    NaughtyOfficer, OfficerPositionGithubTeam, OfficerPositionGithubTeamMapping


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


class NaughtyOfficerAdmin(admin.ModelAdmin):
    list_display = ('sfu_computing_id',)


admin.site.register(NaughtyOfficer, NaughtyOfficerAdmin)
