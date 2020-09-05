from django.apps import AppConfig
from .models import Profile, Trading, Stock
from django.contrib import admin


class MainappConfig(AppConfig):
    name = 'mainapp'

admin.site.register(Profile, Trading, Stock)

