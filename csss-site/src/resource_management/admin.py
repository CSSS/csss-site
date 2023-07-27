from django.contrib import admin

# Register your models here.
from resource_management.models import NonOfficerGoogleDriveUser, GoogleDrivePublicFile, \
    NonOfficerGithubMember, \
    OfficerPositionGithubTeam, OfficerPositionGithubTeamMapping, \
    GoogleDriveNonMediaFileType, MediaToBeMoved, Upload, MediaUpload


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


class GoogleDriveFileTypeAdmin(admin.ModelAdmin):
    list_display = ('mime_type', 'file_extension', 'note')


admin.site.register(GoogleDriveNonMediaFileType, GoogleDriveFileTypeAdmin)


class MediaToBeMovedAdmin(admin.ModelAdmin):
    list_display = ('file_path', 'file_name')


admin.site.register(MediaToBeMoved, MediaToBeMovedAdmin)


class UploadAdmin(admin.ModelAdmin):
    list_display = ('upload_date', 'event_type', 'event_date', 'relevant_note')


admin.site.register(Upload, UploadAdmin)


class MediaUploadAdmin(admin.ModelAdmin):
    list_display = ('media', 'upload')


admin.site.register(MediaUpload, MediaUploadAdmin)
