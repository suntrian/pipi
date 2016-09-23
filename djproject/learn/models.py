from django.db import models
from django.utils import timezone
from datetime import datetime


# Create your models here.


class Persion(models.Model):
    userid = models.AutoField(auto_created=True, primary_key=True)
    username = models.CharField(max_length=20, unique=True)
    nickname = models.CharField(max_length=20)
    head = models.CharField(max_length=100)
    autostart = models.BooleanField(default=True)
    notifytype = models.IntegerField(default=0)
    notifysound = models.BooleanField(default=True)
    notifysoundtypt = models.CharField(max_length=16, default='Glass')
    notifymaxnum = models.IntegerField(default=10)
    notifymaxtime = models.IntegerField(default=10)
    search = models.CharField(max_length=20, default='全部')
    doubleclick = models.BooleanField(default=False)
    screen = models.IntegerField(default=0)
    wallpaper = models.CharField(max_length=255)

    def __str__(self):
        return self.username


class App(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True)
    appid = models.CharField(max_length=30)
    name = models.CharField(max_length=30)
    comment = models.CharField(max_length=100)
    type = models.CharField(max_length=10)
    ico = models.TextField()
    notifys = models.IntegerField(default=0)
    deletable = models.IntegerField(default=0)
    verify = models.IntegerField(default=1)
    command = models.CharField(max_length=200)
    browser = models.CharField(max_length=16, null=True)
    src = models.CharField(max_length=255, null=True)
    maximize = models.IntegerField(default=0)
    width = models.IntegerField(null=True)
    height = models.IntegerField(null=True)

    def __str__(self):
        return self.appid


class UserApps(models.Model):
    uid = models.ForeignKey(Persion)
    aid = models.ForeignKey(App)
    appid = models.CharField(max_length=30, null=True)
    position = models.CharField(max_length=255)


class Config(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True)
    key = models.CharField(max_length=255, unique=True)
    value = models.CharField(max_length=255)
    comment = models.TextField()
    moditime = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.key
