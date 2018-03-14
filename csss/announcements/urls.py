from django.conf.urls import url, include
from django.views.generic import ListView, DetailView
from announcements.models import Post
from django_mailbox.models import Mailbox

mailboxes = Mailbox.active_mailboxes.all()
for mailbox in mailboxes:
  logger.info(
    'Gathering messages for %s',
    mailbox.name
    )
  messages = mailbox.get_new_mail()
  for message in messages:
    logger.info(
      'Received Subject=[%s] From=[%s] From=[%s] Body=[%s]',
      message.subject,
      message.from_header,
      message.from_address,
      message.body
      )

urlpatterns= [
	url(r'^(?P<pk>\d+)$',DetailView.as_view(model=Mailbox,template_name='announcements/post.html' )),
	url(r'^$',ListView.as_view(queryset=Mailbox.objects.all().order_by("date")[:25],template_name="announcements/announcements.html"))
]
