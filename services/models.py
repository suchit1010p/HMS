from django.db import models
from service.models import Students_data

class Service(models.Model):
    img_location = models.TextField()
    icon_name = models.CharField(max_length=100)
    ser_name = models.CharField(max_length=100)
    description = models.TextField()

class Complaint(models.Model):
    COMPLAINT_TYPES = [
        ('room', 'Room'),
        ('bathroom', 'Bathroom'),
        ('furniture', 'Furniture'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]

    student = models.ForeignKey(Students_data, on_delete=models.CASCADE)
    complaint_type = models.CharField(max_length=100, choices=COMPLAINT_TYPES)
    other_type = models.CharField(max_length=100, blank=True, null=True)  # Optional field
    description = models.TextField()
    room_number = models.CharField(max_length=10)
    date_submitted = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.student.user.username} - {self.get_complaint_type_display()} ({self.get_status_display()})"


    
# Create your models here.
