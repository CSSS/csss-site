from django.db import models

# Create your models here.
class DocumentToPull(models.Model):
	name=models.CharField(
		max_length=140,
		default='Document Name',
	)
	fileName = models.CharField(
		max_length=140,
		default='File Name',
	)
	url=models.CharField(
		max_length=2000,
		default='Document URL',
	)
	filePath=models.CharField(
		max_length=500,
		default='Document File Path',
	)

	def __str__(self):
		return self.name