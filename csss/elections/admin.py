from django.contrib import admin

# Register your models here.

from elections.models import NominationPage, Nominee #,Nomination

from django import forms




#admin.site.register(Nomination, NominationAdmin)

@admin.register(NominationPage)
class NominationPageAdmin(admin.ModelAdmin):
	prepopulated_fields = {"slug": ("slugDate","type_of_election",)}

#@admin.register(Nominee)
#class NomineeAdmin(admin.ModelAdmin):

class NomineeForm(forms.ModelForm):
	class Meta:
		model = Nominee
		fields = '__all__'

class NomineeAdmin(admin.ModelAdmin):
	form = NomineeForm
	list_display = ('name', 'Position', 'Speech', 'Facebook', 'LinkedIn', 'Email', 'Discord_Username')

admin.site.register(Nominee, NomineeAdmin)
