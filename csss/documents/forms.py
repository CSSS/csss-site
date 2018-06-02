from django import forms
from documents.models import Upload

class ContactForm(forms.ModelForm):
  title = forms.CharField(required=True)
  contact_info = forms.CharField(required=False)
  additional_info = forms.CharField(required=False)
  pics_from_event = forms.FileField(required=True,
    widget=forms.ClearableFileInput(attrs={'multiple': True}))

  class Meta:
    model = Upload
    fields = ('title', 'contact_info', 'additional_info', 'pics_from_event' )

  def save(self, commit=True):
        upload = super(ContactForm, self).save(commit=False)
        upload.title = self.cleaned_data['title']
        upload.contact_info = self.cleaned_data['contact_info']
        upload.additional_info = self.cleaned_data['additional_info']

        if commit:
            upload.save()

        return upload