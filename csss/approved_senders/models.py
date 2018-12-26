from django.db import models

# Create your models here.
class Sender(models.Model):
	email=models.CharField(max_length=140)
	name=models.CharField(max_length=140)

	def __str__(self):
		return self.email