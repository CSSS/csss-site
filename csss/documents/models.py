from django.db import models

class pictureSubmissions(models.Model):
	EventType = (
		('RE', 'Recurring Events'),
		('Frosh', 'FroshWeek'),
		('SV', 'Silicon Valley'),
		('Hackathon', 'Hackathon'),

		)

	event_date = models.DateField("Date of the Event",default=date.today)
	event_type = models.CharField("Event Type",max_length=9, choices=EventType)
	optional_info = models.TextField("Optional Information",blank=True,max_length=50)

class pictureFiles(models.Model):
	pictureSubmissions = models.ForeignKey('Event Info', on_delete=models.cascade)
	Image = models.ImageField(upload_to='/pictureSubmissions/')