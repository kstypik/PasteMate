from django.contrib import admin

from accounts.models import Preferences, User

admin.site.register(User)
admin.site.register(Preferences)
