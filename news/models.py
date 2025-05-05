from django.db import models
from tinymce.models import HTMLField

class Notice(models.Model):
    notice_title = models.CharField(max_length=50)
    notice_desc = HTMLField()

class Events(models.Model):
    event_title = models.CharField(max_length=50)
    event_desc =  HTMLField()
# Create your models here.
