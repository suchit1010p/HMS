from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .models import Complaint
from service.models import Students_data

from django.db import connection

def reset_complaint_pk_if_empty():
    if Complaint.objects.count() == 0:
        with connection.cursor() as cursor:
            # PostgreSQL / SQLite / MySQL: Reset auto-increment
            db_vendor = connection.vendor
            if db_vendor == 'sqlite':
                cursor.execute("DELETE FROM sqlite_sequence WHERE name='services_complaint';")
            elif db_vendor == 'postgresql':
                cursor.execute("ALTER SEQUENCE services_complaint_id_seq RESTART WITH 1;")
            elif db_vendor == 'mysql':
                cursor.execute("ALTER TABLE services_complaint AUTO_INCREMENT = 1;")


@login_required
def submit_complaint(request):
    if request.method == 'POST':
        complaint_type = request.POST.get('complaint_type')
        other_type = request.POST.get('other_type')
        description = request.POST.get('description')
        room_number = request.POST.get('room_number')

        # Use 'other_type' if complaint_type is 'other'
        final_type = other_type if complaint_type == 'other' else complaint_type

        # Get the Students_data instance for the logged-in user
        try:
            student_data = Students_data.objects.get(user=request.user)
        except Students_data.DoesNotExist:
            return render(request, 'error.html', {'message': 'Student data not found for user.'})

        
        # ✅ Check if table is empty and reset auto-increment if needed
        reset_complaint_pk_if_empty()
        
        
        # Create the complaint
        Complaint.objects.create(
            student=student_data,
            complaint_type=final_type,
            other_type=other_type if complaint_type == 'other' else None,  # Save other_type if complaint_type is 'other'
            description=description,
            room_number=room_number
        )

        return redirect('complaints')  # Adjust the redirect as needed

    return redirect('complaints')


