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
        ('electrical', 'Electrical'),
        ('plumbing', 'Plumbing'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]

    student = models.ForeignKey(Students_data, on_delete=models.CASCADE)
    complaint_type = models.CharField(max_length=100, choices=COMPLAINT_TYPES)
    other_type = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField()
    room_number = models.CharField(max_length=10)
    date_submitted = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.student.user.username} - {self.get_complaint_type_display()} ({self.get_status_display()})"


class Payment(models.Model):
    STATUS_CHOICES = [
        ('created', 'Created'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]

    PAYMENT_TYPE_CHOICES = [
        ('hostel_fee', 'Hostel Fee'),
        ('mess_fee', 'Mess Fee'),
        ('maintenance', 'Maintenance Charge'),
        ('other', 'Other'),
    ]

    student = models.ForeignKey(Students_data, on_delete=models.CASCADE, related_name='payments')
    razorpay_order_id = models.CharField(max_length=100, unique=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=50, choices=PAYMENT_TYPE_CHOICES, default='hostel_fee')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    pdf_path = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.user.username} - ₹{self.amount} ({self.status})"
