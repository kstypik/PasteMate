from django.contrib import admin

from .models import Preferences, User

admin.site.register(User)
admin.site.register(Preferences)
