from django.contrib import admin

from elections.models import Election, Nominee, NomineePosition, NomineeSpeech, NomineeLink


# Register your models here.

class ElectionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'slug',
        'election_type',
        'date',
        'websurvey'
    )


admin.site.register(Election, ElectionAdmin)


class NomineeLinkAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'full_name',
        'election',
        'nominee'
    )


admin.site.register(NomineeLink, NomineeLinkAdmin)


class NomineeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'election',
        'full_name',
        'facebook',
        'linkedin',
        'email',
        'discord',
    )


admin.site.register(Nominee, NomineeAdmin)


class NomineeSpeechAdmin(admin.ModelAdmin):
    list_display = (
        'nominee',
        'speech'
    )


admin.site.register(NomineeSpeech, NomineeSpeechAdmin)


class NomineeOfficerPositionAdmin(admin.ModelAdmin):
    list_display = (
        'nominee',
        'position_name'
    )

    def nominee(self, obj):
        return obj.nominee_speech.nominee

    nominee.short_description = "nominee"
    nominee.admin_order_field = "nominee_speech_id"


admin.site.register(NomineePosition, NomineeOfficerPositionAdmin)
