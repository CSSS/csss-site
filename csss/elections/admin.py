from django.contrib import admin

# Register your models here.

from elections.models import NominationPage, Nominee #,Nomination

from django import forms

@admin.register(NominationPage)
class NominationPageAdmin(admin.ModelAdmin):
	prepopulated_fields = {"slug": ("slugDate","type_of_election",)}


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
