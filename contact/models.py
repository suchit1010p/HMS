from django.db import models

# Create your models here.
class contactus(models.Model):
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    subject = models.CharField(max_length=50)
    description = models.TextField()
    image=models.ImageField(null=True,blank =True, upload_to="media/")