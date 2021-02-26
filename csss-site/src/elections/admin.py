from django.contrib import admin

from elections.models import Election, Nominee, NomineePosition, NomineeSpeech


# Register your models here.


class ElectionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'slug',
        'Election_Type',
        'date',
        'websurvey'
    )

    def Election_Type(self, obj):
        return obj.election_type

    Election_Type.admin_order_field = "election_type"


admin.site.register(Election, ElectionAdmin)


class NomineeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'Election',
        'name',
        'facebook',
        'linked_in',
        'email',
        'discord',
    )

    def Election(self, obj):
        return obj.election

    Election.admin_order_field = "election_id"


admin.site.register(Nominee, NomineeAdmin)


class NomineeSpeechAdmin(admin.ModelAdmin):
    list_display = (
        'Nominee',
        'speech'
    )

    def Nominee(self, obj):
        return obj.nominee

    Nominee.short_description = "Nominee"
    Nominee.admin_order_field = "nominee"


admin.site.register(NomineeSpeech, NomineeSpeechAdmin)


class NomineeOfficerPositionAdmin(admin.ModelAdmin):
    list_display = (
        'Nominee',
        'position_name'
    )

    def Nominee(self, obj):
        return obj.nominee_speech.nominee

    Nominee.short_description = "Nominee"
    Nominee.admin_order_field = "nominee_speech_id"


admin.site.register(NomineePosition, NomineeOfficerPositionAdmin)
