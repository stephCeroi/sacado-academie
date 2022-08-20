from django import forms
from sendmail.models import Email, Communication , Discussion ,  Message
from account.models import User
from socle.models import Subject
from django.forms import models
from django.forms.fields import MultipleChoiceField
 

class EmailForm(forms.ModelForm):

	class Meta:
		model = Email
		fields = ('subject','texte'  )
    
 
 
	def clean(self):
		cleaned_data = super().clean()

		texte = cleaned_data.get("texte")
		subject = cleaned_data.get("subject")

		if texte == "" or subject == ""  :
			msg = "Ces champs ne peuvent être vides"
			self.add_error('texte', msg)
			self.add_error('subject', msg)



class CommunicationForm(forms.ModelForm):

	class Meta:
		model = Communication
		fields = '__all__'



class DiscussionForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		super(DiscussionForm, self).__init__(*args, **kwargs)
		subjects = Subject.objects.filter(is_active=1)
		self.fields['subject']  = forms.ModelChoiceField(queryset=subjects)
	class Meta:
		model = Discussion
		fields = '__all__'



class MessageForm(forms.ModelForm):

	class Meta:
		model = Message
		fields = '__all__'

 
