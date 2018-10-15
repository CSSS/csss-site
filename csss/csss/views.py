from django.shortcuts import render
from announcements.models import Post
import announcements
from django_mailbox.models import Message, Mailbox
import base64
import datetime
import six
from time import strptime
from pytz import timezone

def filterSender(messages):
	theBody=""
	valid_messages = []
	valid_senders = []
	with open("csss/poster.txt", "r") as file:
		for line in file:
			valid_senders.append(line.rstrip().lower())

	for message in messages:
		from_header = str(message.from_header.rstrip())
		for sender in valid_senders:
			if sender in from_header:
				valid_messages.append(message)
				break
	
	return valid_messages;

def extract_sender(from_header):
	indexOfFirst=from_header.index("<")
	return from_header[0:indexOfFirst]

def removePhotoEmails(message):
	if "Subject: [WEBSITE PHOTOS]" in str(message):
		print("email is for the photo gallery")
		return False
	else:
		print("email is for the announcements")
		return True

def remove_tzinfo(date):
	indexBeforeTZINFO=0
	indexesPassed=0
	while True:
		if date[indexBeforeTZINFO] == " ":
			indexesPassed+=1
			if indexesPassed == 5:
				return date[:indexBeforeTZINFO]
		indexBeforeTZINFO+=1

def index(request):
	print("announcements index")
	mailboxes = Mailbox.objects.all()
	for mailbox in mailboxes:
		mailbox.get_new_mail(condition=removePhotoEmails)
	posts = filterSender(Message.objects.all().order_by('-id'))
	for message in posts:

		#will modify the processed date to be change from the day the mailbox was polled to the date the email was sent
		message.processed = datetime.datetime.strptime(remove_tzinfo(message.get_email_object().get('date')),'%a, %d %b %Y %H:%M:%S')
		
		#exracting the snder from the from_header field
		message.from_header = extract_sender(message.from_header)

		#decoding the email body
		message.body = message.html

	for post in Post.objects.all().order_by('-id'):
		posts.append(post)

	posts.sort(key=lambda x: x.processed, reverse=True)

	return render(request, 'announcements/announcements.html', {'posts': posts})

def contact(request):
	return render(request, 'csss/basic.html', {'content':['If you would like to contact me, please email me', 'csss-webmaster@sfu.ca']})
