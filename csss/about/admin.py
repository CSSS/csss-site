from django.contrib import admin

# Register your models here.

from about.models import Officer, Term #, FavCourse, FavLanguage

from django import forms


class TermForm(forms.ModelForm):
	class Meta:
		model = Term
		fields = '__all__'

	def clean(self):
		print("self.cleaned_data="+str(self.cleaned_data))
		term = self.cleaned_data.get('term')
		year = self.cleaned_data.get('year')
		position=0
		if term == 'Fall':
			position = ( year * 10 ) + 3
		elif term == 'Spring':
			position = ( year * 10 ) + 1
		elif term == 'Summer':
			position = ( year * 10 ) + 2
		

		if len(Term.objects.all().filter(position=position)) is not 0:
			raise forms.ValidationError("That object could not be created as it is not unique" )

		return self.cleaned_data

	def save(self, commit=True):
		if self.instance.term == 'Fall':
			self.instance.position = ( self.instance.year * 10 ) + 3
		elif self.instance.term == 'Spring':
			self.instance.position = ( self.instance.year * 10 ) + 1
		elif self.instance.term == 'Summer':
			self.instance.position = ( self.instance.year * 10 ) + 2

		if self.errors:
			raise ValueError(
				"The %s could not be %s because the data didn't validate." % (
					self.instance._meta.object_name,
					'created' if self.instance._state.adding else 'changed',
				)
			)		
		if commit:
			self.instance.save()
			self._save_m2m()
		else:
			self.save_m2m = self._save_m2m
		return self.instance

class TermAdmin(admin.ModelAdmin):
	form = TermForm
	list_display = ('position', 'term', 'year', )

admin.site.register(Term, TermAdmin)


class OfficerForm(forms.ModelForm):
	class Meta:
		model = Officer
		fields = '__all__' # Or a list of the fields that you want to include in your form

	def save(self, commit=True):
		if self.instance.elected_positions == 'President':
			self.instance.index = (self.instance.elected_term.position*100)+1
		elif self.instance.elected_positions == 'Vice-President':
			self.instance.index = (self.instance.elected_term.position*100)+2
		elif self.instance.elected_positions == 'Treasurer':
			self.instance.index = (self.instance.elected_term.position*100)+3
		elif self.instance.elected_positions == 'Director of Communications':
			self.instance.index = (self.instance.elected_term.position*100)+4
		elif self.instance.elected_positions == 'Director of Events':
			self.instance.index = (self.instance.elected_term.position*100)+5
		elif self.instance.elected_positions == 'Director of Resources':
			self.instance.index = (self.instance.elected_term.position*100)+6
		elif self.instance.elected_positions == 'Director of Archives':
			self.instance.index = (self.instance.elected_term.position*100)+7
		elif self.instance.elected_positions == 'Secretary':
			self.instance.index = (self.instance.elected_term.position*100)+8
		elif self.instance.elected_positions == 'Director of Activities':
			self.instance.index = (self.instance.elected_term.position*100)+9
		elif self.instance.elected_positions == 'Councilor':
			self.instance.index = (self.instance.elected_term.position*100)+10
		elif self.instance.elected_positions == 'Exec-at-Large 1':
			self.instance.index = (self.instance.elected_term.position*100)+11
		elif self.instance.elected_positions == 'Exec-at-Large 2':
			self.instance.index = (self.instance.elected_term.position*100)+12
		elif self.instance.elected_positions == 'First Year Representative 1':
			self.instance.index = (self.instance.elected_term.position*100)+13
		elif self.instance.elected_positions == 'First Year Representative 2':
			self.instance.index = (self.instance.elected_term.position*100)+14
		elif self.instance.elected_positions == 'Council Representative':
			self.instance.index = (self.instance.elected_term.position*100)+15
		elif self.instance.elected_positions == 'Election Officer':
			self.instance.index = (self.instance.elected_term.position*100)+16
		elif self.instance.elected_positions == 'Frosh Week Chair':
			self.instance.index = (self.instance.elected_term.position*100)+17

		if self.errors:
			raise ValueError(
				"The %s could not be %s because the data didn't validate." % (
					self.instance._meta.object_name,
					'created' if self.instance._state.adding else 'changed',
				)
			)		
		if commit:
			self.instance.save()
			self._save_m2m()
		else:
			self.save_m2m = self._save_m2m
		return self.instance


class OfficerAdmin(admin.ModelAdmin):
	form = OfficerForm
	list_display = ('index','elected_term','elected_positions','Name', 'Bio', 'course1', 'course2', 'language1', 'language2' )

admin.site.register(Officer, OfficerAdmin)