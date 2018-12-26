from django.contrib import admin

# Register your models here.

from about.models import Officer#, FavCourse, FavLanguage

from django import forms

class OfficerForm(forms.ModelForm):
	class Meta:
		model = Officer
		fields = '__all__' # Or a list of the fields that you want to include in your form
	def clean(self):
		term_year = self.cleaned_data.get('term_year')
		if term_year < 1966:
			raise forms.ValidationError("Invalid Term Year")
		return self.cleaned_data

class OfficerAdmin(admin.ModelAdmin):
	form = OfficerForm
	list_display = ('Name', 'Bio', 'course1', 'course2', 'language1', 'language2', 'position','term', 'term_year')

admin.site.register(Officer, OfficerAdmin)