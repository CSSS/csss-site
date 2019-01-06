# Register your models here.
from django.contrib import admin
from documents.models import DocumentToPull
from django.utils.translation import ugettext_lazy as _

import requests, shutil
# Register your models here.

def get_new_mail(mailbox_admin, request, queryset):
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


get_new_mail.short_description = _('Poll Document')

class DocumentAdmin(admin.ModelAdmin):
	list_display = (
		'name',
		'fileName',
		'url',
		'filePath',
	)
	actions = [get_new_mail]

admin.site.register(DocumentToPull, DocumentAdmin)