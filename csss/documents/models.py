from django.db import models

from django import forms

class documentsPage(models.Model):
	title=models.CharField(max_length=140)
	body=models.TextField()

	def __str__(self):
		return self.title
# Create your models here.

class ContactForm(forms.Form):
  contact_name = forms.CharField(required=True)
  content = forms.CharField(
    required = True,
    widget=forms.Textarea
  )