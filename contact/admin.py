from django.contrib import admin
from contact.models import contactus

class contact(admin.ModelAdmin):   
    list_display=('name','email','phone','subject','description','image')

admin.site.register(contactus,contact)
# Register your models here.


  
        
