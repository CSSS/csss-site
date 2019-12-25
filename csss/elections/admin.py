from django.contrib import admin

# Register your models here.

from elections.models import NominationPage, Nominee #,Nomination

from django import forms

class NominationPageAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'slug',
	'get_type_of_election',
	'datePublic',
        'websurvey'
    )

    def get_type_of_election(self, obj):
        return obj.type_of_election 
    get_type_of_election.short_desription = "Election Type"
    get_type_of_election.admin_order_field = "Election Type"

admin.site.register(NominationPage, NominationPageAdmin)


class NomineeForm(forms.ModelForm):
	class Meta:
		model = Nominee
		fields = '__all__'

class NomineeAdmin(admin.ModelAdmin):
    form = NomineeForm
    list_display = ('name', 'Position', 'Speech', 'Facebook', 'LinkedIn', 'Email', 'Discord_Username', 'get_election')

    def get_election(self, obj):
        return obj.nominationPage
    get_election.short_description = "Election"
    get_election.admin_order_field = "Election"

admin.site.register(Nominee, NomineeAdmin)
