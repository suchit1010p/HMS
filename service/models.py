from django.db import models
from django.contrib.auth.models import User

class Room(models.Model):
    room_number = models.CharField(max_length=10, unique=True)
    floor_number = models.IntegerField()
    capacity = models.IntegerField(default=4)

    def __str__(self):
        return f"Room {self.room_number}"

    @property
    def available_slots(self):
        return self.capacity - self.students.count()


class Students_data(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)  # Link to Django's User model
    phone = models.CharField(max_length=15, unique=True)
    dob = models.DateField()
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip = models.CharField(max_length=10, unique=True)
    university = models.CharField(max_length=100)
    enrollmentYear = models.IntegerField()
    course = models.CharField(max_length=100)
    programDuration = models.IntegerField()
    is_active = models.BooleanField(default=True)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')

    def __str__(self):
        return f"{self.user.username} - {self.course}"
