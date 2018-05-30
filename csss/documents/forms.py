from django import forms

class ContactForm(forms.ModelForm):
  contact_name = forms.CharField(required=True)
  content = forms.CharField(
    required = True,
    widget=forms.Textarea
  )
  pics_from_event = forms.FileField(required=False,
    widget=forms.ClearableFileInput(attrs={'multiple': True}))

  def save(self, commit=True):
  	name = self.cleaned_data['contact_name']
  	content = self.cleaned_data['content']

