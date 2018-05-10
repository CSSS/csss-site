from django.db import models

class Post(models.Model):
	title=models.CharField(max_length=140)
	body=models.TextField()
	date=models.DateTimeField()
	from_header=models.CharField(max_length=140)
	def __str__ (self):
		return self.title

# Create your models here.
