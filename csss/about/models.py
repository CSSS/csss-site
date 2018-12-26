from django.db import models
from django.utils.translation import ugettext_lazy as _


class aboutPage(models.Model):
	title=models.CharField(max_length=140)
	body=models.TextField()

	def __str__(self):
		return self.title
# Create your models here.

class Officer(models.Model):
	Name = models.CharField(max_length=140)
	Bio = models.CharField(max_length=2000)
	course1 = models.CharField(_(u'First Favorite Course'),max_length=10)
	course2 = models.CharField(_(u'Second Favorite Course'),max_length=10)
	language1 = models.CharField(_(u'First Favorite Language'),max_length=10)
	language2 = models.CharField(_(u'Second Favorite Language'),max_length=10)
	position_choices = (
		('President', 'President'),
		('Vice-President', 'Vice-President'),
		('Treasurer', 'Treasurer'),
		('DoE', 'Direcor of Events'),
		('DoA', 'Director of Archives'),
		('DoC', 'Director of Communications'),
		('DoR', 'Director of Resources'),
		('EAL1', 'Exec-at-Large 1'),
		('EAL2', 'Exec-at-Large 2'),
		('FYR1', 'First Year Representative'),
		('FYR2', 'First Year Representative'),
		('CouncilRep', 'Council Representative'),
		('ElectionOfficer', 'Election Officer'),
		('FroshChair', 'Frosh Week Chair'),
	)
	position = models.CharField(
		max_length=15,
		choices=position_choices,
		default='President',
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
	)
	term_year = models.IntegerField(_(u'Term Year'),default='2018')
	image = models.CharField(_(u'Link to Profile Picture'),max_length=400)
	def __str__(self):
		return self.Name

#class FavCourse(models.Model):
#	Officer = models.ForeignKey(Officer, related_name='officer', on_delete=models.CASCADE)
#	course = models.CharField(max_length=10)
#
#class FavLanguage(models.Model):
#	Officer = models.ForeignKey(Officer, related_name='officer', on_delete=models.CASCADE)
#	language = models.CharField(max_length=10)