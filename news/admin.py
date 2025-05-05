from django.contrib import admin
from news.models import Notice,Events

class notice_admin(admin.ModelAdmin):
    list_display = ('notice_title','notice_desc')
    
admin.site.register(Notice, notice_admin)

class event_admin(admin.ModelAdmin):
    list_display = ('event_title','event_desc')

admin.site.register(Events, event_admin)
# Register your models here.
