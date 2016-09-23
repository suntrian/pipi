from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import App
from .models import Config

admin.site.register(App)
admin.site.register(Config)
