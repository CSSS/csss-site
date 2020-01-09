from django.contrib import admin

# Register your models here.
from administration.models import OfficerUpdatePassphrase

class OfficerUpdatePassphraseAdmin(admin.ModelAdmin):
    # form = OfficerForm
    list_display = ('passphrase','used')

admin.site.register(OfficerUpdatePassphrase, OfficerUpdatePassphraseAdmin)
