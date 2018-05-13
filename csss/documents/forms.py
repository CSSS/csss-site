from django import forms

class ContactForm(forms.Form):
  contact_name = forms.CharField(required=True)
  content = forms.CharField(
    required = True,
    widget=forms.Textarea
  )
  pics_from_event = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))