from django.shortcuts import render
from announcements.models import Post
import announcements

def index(request):
	print("announcements index")
	object_list = Post.objects.all()
	return render(request, 'announcements/announcements.html', {'object_list': object_list})
#	return render(request, 'announcements/announcements.html', {'content':['Hi you doiiiiiin?']})

def contact(request):
	return render(request, 'csss/basic.html', {'content':['If you would like to contact me, please email me', 'csss-webmaster@sfu.ca']})
