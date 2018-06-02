from django import forms
from documents.models import Upload
class ContactForm(forms.ModelForm):
  contact_name = forms.CharField(required=True)
  content = forms.CharField(
    required = True,
    widget=forms.Textarea
  )
  pics_from_event = forms.FileField(required=False,
    widget=forms.ClearableFileInput(attrs={'multiple': True}))

  class Meta:
    model = Upload
    fields = ('upload',)