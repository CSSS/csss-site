from django.db import models
from django.utils.translation import ugettext_lazy as _
import datetime

class aboutPage(models.Model):
	title=models.CharField(max_length=140)
	body=models.TextField()

	def __str__(self):
		return self.title
# Create your models here.

class Term(models.Model):
	position = models.IntegerField(
		primary_key=True,
		default=666,
	)
	term_choices = (
		('Fall', 'Fall'),
		('Spring', 'Spring'),
		('Summer', 'Summer'),
	)
	term = models.CharField(
		max_length=6,
		choices=term_choices,
		default='Fall',
		help_text = _("You need to click on the dropbox above in order for the slug field to get populated"),
	)
	
	year = models.IntegerField(
		choices=[ (b,b) for b in list(reversed(range(1970, datetime.datetime.now().year+1))) ],
		default='2018',
		help_text = _("You need to click on the dropbox above in order for the slug field to get populated"),
	)
	def __str__(self):
		return self.term +" "+str(self.year)

class Officer(models.Model):
	elected_term = models.ForeignKey(
		Term, 
		on_delete=models.CASCADE,
	)
	index = models.IntegerField(
		primary_key=True,
		default=666,
	)
	Name = models.CharField(max_length=140)
	Bio = models.CharField(max_length=2000)
	course1 = models.CharField(
		_(u'First Favorite Course'),
		max_length=10,
	)
	course2 = models.CharField(
		_(u'Second Favorite Course'),
		max_length=10,
	)
	language1 = models.CharField(
		_(u'First Favorite Language'),
		max_length=10,
	)
	language2 = models.CharField(
		_(u'Second Favorite Language'),
		max_length=10,
	)
	elected_positions_choices = (
		('President', 'President'),
		('Vice-President', 'Vice-President'),
		('Treasurer', 'Treasurer'),
		('Director of Events', 'Director of Events'),
		('Director of Archives', 'Director of Archives'),
		('Secretary', 'Secretary'),
		('Director of Activities', 'Director of Activities'),
		('Councilor', 'Councilor'),
		('Director of Communications', 'Director of Communications'),
		('Director of Resources', 'Director of Resources'),
		('Exec-at-Large 1', 'Exec-at-Large 1'),
		('Exec-at-Large 2', 'Exec-at-Large 2'),
		('First Year Representative 1', 'First Year Representative 1'),
		('First Year Representative 2', 'First Year Representative 2'),
		('Council Representative', 'Council Representative'),
		('Election Officer', 'Election Officer'),
		('Frosh Week Chair', 'Frosh Week Chair'),
	)
	elected_positions = models.CharField(
		max_length=27,
		choices=elected_positions_choices,
		default='President',
	)
	image = models.CharField(_(u'Link to Profile Picture'),max_length=400,default='NA')
	def __str__(self):
		return self.Name

#class FavCourse(models.Model):
#	Officer = models.ForeignKey(Officer, related_name='officer', on_delete=models.CASCADE)
#	course = models.CharField(max_length=10)
#
#class FavLanguage(models.Model):
#	Officer = models.ForeignKey(Officer, related_name='officer', on_delete=models.CASCADE)
#	language = models.CharField(max_length=10)