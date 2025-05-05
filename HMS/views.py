from django.shortcuts import render, redirect
from service.models import Students_data
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib import messages
from fpdf import FPDF
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from service.views import allocate_room_to_student
from services.models import Complaint
import qrcode
import tempfile
import os
from services.models import Service
from news.models import Notice, Events
from contact.models import contactus

def home(request):
    servicedata = Service.objects.all()[:6]
    
    context = {
        'servicedata': servicedata,
         }
    
    return render(request, "index.html", context)


def user_login(request):
    servicedata = Service.objects.all()[:6]

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('login')
    
    context = {
        'servicedata': servicedata
    }
    return render(request, 'login.html', context)

def saveEnquiry(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        image = request.FILES.get('image')
        data = contactus(name=name, email=email, phone=phone, subject=subject, description=message, image=image)
        data.save()
        return redirect('/')
    
def RegisterNewStudent(request):
    if request.method == 'POST':
        first_name = request.POST.get('firstName')
        last_name = request.POST.get('lastName')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        dob = request.POST.get('dob')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip = request.POST.get('zip')
        university = request.POST.get('university')
        enrollmentYear = request.POST.get('enrollmentYear')
        course = request.POST.get('course')
        programDuration = request.POST.get('programDuration')
        username = request.POST.get('username')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return redirect('register')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Create an instance of Students_data
        student = Students_data(
            user=user,
            phone=phone,
            dob=dob,
            address=address,
            city=city,
            state=state,
            zip=zip,
            university=university,
            enrollmentYear=enrollmentYear,
            course=course,
            programDuration=programDuration
        )

        # Allocate room to the student (assuming you have a function for this)
        allocate_room_to_student(student)
        # Save the instance to the database
        student.save()
        login(request, user)
        return redirect('dashboard')
    
    return render(request, 'login.html')

@login_required
def dashboard(request):
    student = Students_data.objects.filter(user=request.user).first()
    room = student.room if student and student.room else None
    student_data = None  # Define it upfront
    active_complaints_count = 0 
    if student:
        student_data = {
            "Name": request.user.first_name,
            "Email": request.user.email,
            "Phone": student.phone,
            "dob": student.dob,
            "Address": student.address,
            "City": student.city,
            "State": student.state,
            "ZIP": student.zip,
            "University": student.university,
            "Enrollment_Year": student.enrollmentYear,
            "Course": student.course,
            "Program_Duration": student.programDuration,
            "Username": request.user.username,
            "Room": room.room_number if room else "Not Allocated",
        }
    
    active_complaints_count = Complaint.objects.filter(student=student).count()

    return render(request, 'dashboard/dashboard.html', {'student_data': student_data,'active_complaints_count': active_complaints_count})

def complaints(request):
    complaints = Complaint.objects.filter(student__user=request.user).order_by('-date_submitted')
    context = {
        'complaints': [
            {
                'id': complaint.id,
                'status': complaint.status,
                'complaint_type': complaint.complaint_type,
                'date_submitted': complaint.date_submitted,
            }
            for complaint in complaints
        ],
    }
    return render(request, 'dashboard/complaints.html', context)

def payments(request):
    return render(request, 'dashboard/payments.html')

def profile(request):
    return render(request, 'dashboard/profile.html')

def settings(request):
    return render(request, 'dashboard/settings.html')

def documents(request):
    Eventdata = Events.objects.all()[:6]
    Noticedata = Notice.objects.all()[:6]
    context = {
        'Noticedata': Noticedata,
        'Eventdata': Eventdata,
    }
    return render(request, 'dashboard/documents.html',context)

from django.contrib.auth import logout

def user_logout(request):
    logout(request)
    return redirect('login')

def success(request):
    return render(request, 'successful_registration.html')


class PDF(FPDF):
    def header(self):
        self.image("static/media/logo.jpg", x=90, y=10, w=30)
        self.ln(25)
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Hostel Fees Receipt', ln=True, align='C')
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

def generate_student_pdf(request):
    try:
        student = Students_data.objects.filter(user=request.user).first()
        room = student.room if student and student.room else None
    except Students_data.DoesNotExist:
        return HttpResponse("Student data not found.", status=404)

    # Generate QR code and save to a temp file
    qr_data = f"Name: {User.first_name}\nEmail: {User.email}\nEnrollment Year: {student.enrollmentYear}"
    qr_img = qrcode.make(qr_data)

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as qr_temp:
        qr_img.save(qr_temp.name)
        qr_path = qr_temp.name

    student_dict = {
        "Name": request.user.first_name,
        "Email": request.user.email,
        "Phone": student.phone,
        "Date of Birth": student.dob,
        "Address": student.address,
        "City": student.city,
        "State": student.state,
        "ZIP": student.zip,
        "University": student.university,
        "Enrollment Year": student.enrollmentYear,
        "Course": student.course,
        "Program Duration": student.programDuration,
        "Room Number": room.room_number if room else "Not Allocated",
        "fees-paid": "5000/-",
    }

    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)

    # Table formatting
    pdf.set_fill_color(245, 245, 245)
    row_height = 10

    for key, value in student_dict.items():
        pdf.set_font("Arial", 'B', 11)
        pdf.set_fill_color(220, 220, 220)
        pdf.cell(60, row_height, key, border=1, fill=True)
        pdf.set_font("Arial", '', 11)
        pdf.cell(130, row_height, str(value), border=1)
        pdf.ln()

    # Insert QR code
    pdf.image(qr_path, x=160, y=pdf.get_y() + 5, w=30)

    # Remove temp QR file AFTER using it
    if os.path.exists(qr_path):
        os.remove(qr_path)

    # Return the PDF as response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="fees-receipt.pdf"'
    response.write(pdf.output(dest='S').encode('latin1'))

    return response