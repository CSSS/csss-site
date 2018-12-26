from django.contrib import admin

# Register your models here.
from approved_senders.models import Sender
# Register your models here.

#admin.site.register(Sender)


from django import forms

class SenderForm(forms.ModelForm):
	class Meta:
		model = Sender
		fields = '__all__' # Or a list of the fields that you want to include in your form

	def clean(self):
		email = self.cleaned_data.get('email')
		posOfAt = email.find('@')
		if posOfAt == -1:
			raise forms.ValidationError("Invalid Email, no \"@\" detected")
		posOfDot = email.find('.',posOfAt)
		if posOfDot == -1:
			raise forms.ValidationError("Invalid Email, no period was detected after the \"#\"")
		name = self.cleaned_data.get('name')
		if name == '':
			raise forms.ValidationError("No Name Detected")
		return self.cleaned_data


class SenderAdmin(admin.ModelAdmin):
	form = SenderForm
	list_display = ('email','name')

admin.site.register(Sender, SenderAdmin)