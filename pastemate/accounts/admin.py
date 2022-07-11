from django.contrib import admin

from pastemate.accounts.models import Preferences, User

admin.site.register(User)
admin.site.register(Preferences)
