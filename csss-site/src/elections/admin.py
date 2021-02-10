from django.contrib import admin

# Register your models here.

from elections.models import Election, Nominee, NomineePosition  # ,Nomination

from django import forms


class ElectionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'slug',
        'get_election_type',
        'date',
        'websurvey'
    )

    def get_election_type(self, obj):
        return obj.election_type

    get_election_type.short_desription = "Election Type"
    get_election_type.admin_order_field = "Election Type"


admin.site.register(Election, ElectionAdmin)


class NomineeForm(forms.ModelForm):
    class Meta:
        model = Nominee
        fields = '__all__'


class NomineeAdmin(admin.ModelAdmin):
    form = NomineeForm
    list_display = (
        'id',
        'get_election',
        'name',
        'facebook',
        'linked_in',
        'email',
        'discord',
    )

    def get_election(self, obj):
        return obj.election

    get_election.short_description = "Election"
    get_election.admin_order_field = "Election"


admin.site.register(Nominee, NomineeAdmin)


class NomineeOfficerPositionAdmin(admin.ModelAdmin):
    list_display = (
        'nominee',
        'position_name'
    )


admin.site.register(NomineePosition, NomineeOfficerPositionAdmin)
