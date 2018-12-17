from django.db import models
import datetime
from django.utils import timezone

class pictureSubmissions(models.Model):
	EventType = (
		('RE', 'Recurring Events'),
		('Frosh', 'FroshWeek'),
		('SV', 'Silicon Valley'),
		('Hackathon', 'Hackathon'),
		)

	event_date = models.DateField("Date of the Event",default=timezone.now)
	event_type = models.CharField("Event Type",max_length=9, choices=EventType)
	optional_info = models.TextField("Optional Information",blank=True,max_length=50)

class pictureFiles(models.Model):
	pictureSubmissions = models.ForeignKey('pictureSubmissions', on_delete=models.CASCADE,related_name='pictures',related_query_name='picture')
	Image = models.ImageField(upload_to='pictureSubmissions/')