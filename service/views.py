from django.shortcuts import render
from .models import Room, Students_data

def allocate_room_to_student(student):
    for room in Room.objects.all():
        if room.available_slots > 0:
            student.room = room
            student.save()
            return True  # Room successfully allocated
    return False  # No available room found


# Create your views here.
