# Register your models here.
from django.contrib import admin
from documents.models import DocumentToPull, Repo, Media, Picture, Video, Album, Event, SubCategory
from django.utils.translation import ugettext_lazy as _
import subprocess
import os
import requests, shutil
import os
import datetime
import time
# Register your models here.

def get_update_documents(mailbox_admin, request, queryset):
	for document in queryset.all():
		print('Receiving mail for %s' % document)
		#response = urllib2.urlopen(document.url)
		#file = open(document.filePath+"/"+document.name, 'w')
		#file.write(response.read())
		#file.close()


		#response = requests.get(document.url)
		#with open(document.filePath+"/"+document.name, 'wb') as f:
		#	f.write(response.content)
		#open(document.filePath+"/"+document.name , 'wb').write(r.content)


		#from pathlib import Path
		#import requests
		#filename = Path(document.filePath+"/"+document.name)
		#url = document.url
		#response = requests.get(url)
		#filename.write_bytes(response.content)

		import urllib3
		urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

		import requests
		url=document.url    #Note: It's https
		r = requests.get(url, verify=False,stream=True)
		r.raw.decode_content = True
		with open(document.filePath+"/"+document.fileName , 'wb') as f:
			shutil.copyfileobj(r.raw, f)

		import wget

		#print('\nBeginning file download with wget module\n')

		url = document.url
		wget.download(url, document.filePath+"/"+document.fileName)

get_update_documents.short_description = _('Poll Document')

subcategories = []
path_to_file = ['documents_static', 'event-photos']

class DocumentAdmin(admin.ModelAdmin):
	list_display = (
		'name',
		'fileName',
		'url',
		'filePath',
	)
	actions = [get_update_documents]

def goThroughYouTubeLinks(albumPath, event_name, album_date, album_name):
	file = open(albumPath, "r")
	for link in file:
		link = link.rstrip()
		if link != '':
			eventKey = Event.objects.get(event_name=event_name)
			albumKey = Album.objects.get(date=album_date, name=album_name)

			retrievedObjects = Video.objects.all().filter(youtube_link=link)
			if len(retrievedObjects) == 0:
				videoInst = Video(youtube_link=link)
				videoInst.save()
			else:
				videoInst = retrievedObjects[0]

			retrievedObjects = Media.objects.all().filter(event=eventKey, album_link=albumKey,video=videoInst)
			if len(retrievedObjects) == 0:
				itemInstance = Media(event=eventKey, album_link=albumKey,video=videoInst)
				itemInstance.save()
			else:
				itemInstance = retrievedObjects[0]

			itemSubCategories = subcategories.copy()
			lvl=0
			while len(itemSubCategories) != 0:
				if len(SubCategory.objects.all().filter(media=itemInstance, level=lvl+1, name=itemSubCategories[0])) == 0:
					subCategoryInt = SubCategory(media=itemInstance, level=lvl+1, name=itemSubCategories[0])
					subCategoryInt.save()
				itemSubCategories.pop(0)
				lvl+=1
	file.close()

def iterateThroughMediaForSpecifiAlbum(path_to_file, albumPath, event_name, album_date, album_name):
	albumContents = os.listdir(albumPath)
	for media in albumContents:
		path_to_file.append(media)
		if os.path.isdir(albumPath+'/'+media):
			subcategories.append(media)
			iterateThroughMediaForSpecifiAlbum(path_to_file, albumPath+'/'+media, event_name, album_date, album_name)
			subcategories.pop()
		else:
			if media == 'videos.txt':
				goThroughYouTubeLinks(albumPath+'/'+media, event_name, album_date, album_name)

			elif media[0] != '.':
				file_location = albumPath+'/'+media
				eventKey = Event.objects.get(event_name=event_name)
				albumKey = Album.objects.get(date=album_date, name=album_name)

				retrievedObjects = Picture.objects.all().filter(absolute_file_path=file_location, static_path="/".join(path_to_file))
				if len(retrievedObjects) == 0:
					pictureInstance = Picture(absolute_file_path=file_location, static_path="/".join(path_to_file))
					pictureInstance.save()
				else:
					pictureInstance = retrievedObjects[0]

				retrievedObjects = Media.objects.all().filter(name=media, event=eventKey, album_link=albumKey, picture=pictureInstance)
				if len(retrievedObjects) == 0:
					itemInstance = Media(name=media, event=eventKey, album_link=albumKey, picture=pictureInstance)
					itemInstance.save()
				else:
					itemInstance = retrievedObjects[0]

				if albumKey.album_thumbnail is None:
					albumKey.album_thumbnail = itemInstance
					albumKey.save()
				itemSubCategories = subcategories.copy()
				lvl=0
				while len(itemSubCategories) != 0:
					if len(SubCategory.objects.all().filter(media=itemInstance, level=lvl+1, name=itemSubCategories[0])) == 0:
						subCategoryInt = SubCategory(media=itemInstance, level=lvl+1, name=itemSubCategories[0])
						subCategoryInt.save()
					itemSubCategories.pop(0)
					lvl+=1
		path_to_file.pop()


def createPicturesFromRepo(repo_dir):
	folder_contents = os.listdir(repo_dir)
	for eventName in folder_contents:
		eventPath=repo_dir+eventName
		if os.path.isdir(eventPath) and eventName[0] != '.' :
			path_to_file.append(eventName)
			event_name=eventName
			retrievedObjects = Event.objects.all().filter(event_name=event_name)
			if len(retrievedObjects) == 0:
				event = Event(event_name=eventName)
				event.save()
			else:
				event = retrievedObjects[0]
			albums = os.listdir(eventPath)
			for album in albums:
				if album[0] != '.':
					path_to_file.append(album)
					album_date = ''
					album_name = ''
					if ' ' in album: #there is a name for the album as well as a date
						indexOfSpace = album.find(' ')
						date_of_file=album[0:indexOfSpace]
						if '-' in date_of_file: # in this case, the albumName has the following format "YYYY-MM-DDD <albumName>"
							firstDash=date_of_file.find('-')
							secondDash=date_of_file.find('-',firstDash+1)
							date_of_file = datetime.datetime(int(date_of_file[0:firstDash]), int(date_of_file[firstDash+1:secondDash]), int(date_of_file[secondDash+1:]))
							albumName = album[indexOfSpace+1:]
							album_date = date_of_file
							album_name = albumName
							if len(Album.objects.all().filter(date=date_of_file, name=albumName, event=event)) == 0:
								albumInst = Album(date=date_of_file, name=albumName, event=event)
								albumInst.save()
						else: # in this case, the albumName has the following format "YYYY <albumName>"
							date_of_file = datetime.datetime(int(date_of_file), 1, 1)
							albumName = album[indexOfSpace+1:]
							album_date = date_of_file
							album_name = albumName
							if len(Album.objects.all().filter(date=date_of_file, name=albumName, event=event)) == 0:
								albumInst = Album(date=date_of_file, name=albumName, event=event)
								albumInst.save()
					else: #there is no name in the album folder
						if '-' in album: # in this case, the albumName has the following format "YYYY-MM-DDD"
							firstDash=album.find('-')
							secondDash=album.find('-',firstDash+1)
							date_of_file = datetime.datetime(int(album[0:firstDash]), int(album[firstDash+1:secondDash]), int(album[secondDash+1:]))
							album_date = date_of_file
							if len(Album.objects.all().filter(date=date_of_file, event=event)) == 0:
								albumInst = Album(date=date_of_file, event=event)
								albumInst.save()
						else: # in this case, the albumName has the following format "YYYY"
							date_of_file = datetime.datetime(int(album), 1, 1)
							album_date = date_of_file
							album_name = albumName
							if len(Album.objects.all().filter(date=date_of_file, event=event)) == 0:
								albumInst = Album(date=date_of_file, event=event)
								albumInst.save()
					albumPath = "{0}/{1}".format(eventPath,album)
					files = os.listdir(albumPath)
					iterateThroughMediaForSpecifiAlbum(path_to_file, albumPath, event_name, album_date, album_name)
					path_to_file.pop()
			path_to_file.pop()

def clone_repos(mailbox_admin, request, queryset):
	for repo in queryset.all():
		print('doing a git pull inside of {0}'.format(repo.url))
		commands='cd {0}; git pull'.format(repo.absolute_path)
		exitCode, output = subprocess.getstatusoutput(commands)
		print("exitCode={0} and output={1}".format(exitCode, output))
		createPicturesFromRepo(repo.absolute_path)


clone_repos.short_description = _('Git Pull')

class RepoAdmin(admin.ModelAdmin):
	list_display = (
	'name',
	'url',
	'absolute_path',
	'static_path'
	)
	actions = [clone_repos]

class EventAdmin(admin.ModelAdmin):
	list_display = (
	'event_name',
	)

class AlbumAdmin(admin.ModelAdmin):
	list_display = (
	'event',
	'date',
	'name',
	'album_thumbnail'
	)

class MediaAdmin(admin.ModelAdmin):
	list_display = (
	'id',
	'event',
	'album_link',
	'name',
	'picture',
	'video'
	)

class PictureAdmin(admin.ModelAdmin):
	list_display = (
	'absolute_file_path',
	'static_path'
	)

class VideoAdmin(admin.ModelAdmin):
	list_display = (
	'youtube_link',
	)

class SubCategoryAdmin(admin.ModelAdmin):
	list_display = (
	'media',
	'level',
	'name'
	)


admin.site.register(DocumentToPull, DocumentAdmin)
admin.site.register(Repo, RepoAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Album, AlbumAdmin)
admin.site.register(Media, MediaAdmin)
admin.site.register(Picture, PictureAdmin)
admin.site.register(Video, VideoAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
