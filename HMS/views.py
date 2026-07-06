from django.shortcuts import render, redirect
from service.models import Students_data
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from fpdf import FPDF
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from service.views import allocate_room_to_student
from services.models import Complaint, Payment
import qrcode
import tempfile
import os
import hmac
import hashlib
import razorpay
from django.conf import settings
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from services.models import Service
from news.models import Notice, Events
from contact.models import contactus
import json
import random
import io
import requests
from twilio.rest import Client


def send_otp_sms(phone_number, otp, purpose='OTP', fallback_email=None):
    """
    Send OTP via SMS to any Indian number.
    Priority: Fast2SMS (free, any number) → Twilio → Email fallback.
    Returns (success: bool, method_used: str, error_msg: str|None)
    """
    message_body = f"Your HMS {purpose} OTP is: {otp}. Valid for 5 minutes. Do not share this with anyone."

    # ── 1. Try Fast2SMS (works with any Indian number, no verification needed) ──
    fast2sms_key = getattr(settings, 'FAST2SMS_API_KEY', '')
    if fast2sms_key and fast2sms_key != 'YOUR_FAST2SMS_API_KEY_HERE':
        # Strip +91 prefix — Fast2SMS expects 10-digit number only
        number = phone_number.replace('+91', '').replace('+', '').strip()
        try:
            resp = requests.post(
                'https://www.fast2sms.com/dev/bulkV2',
                headers={'authorization': fast2sms_key},
                data={
                    'route': 'otp',
                    'variables_values': otp,
                    'flash': 0,
                    'numbers': number,
                },
                timeout=10
            )
            result = resp.json()
            if result.get('return') is True:
                return True, 'fast2sms', None
            else:
                fast2sms_error = result.get('message', 'Fast2SMS unknown error')
        except Exception as e:
            fast2sms_error = str(e)
    else:
        fast2sms_error = 'Fast2SMS API key not configured'

    # ── 2. Try Twilio (fallback — trial only sends to verified numbers) ──
    twilio_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
    twilio_token = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
    twilio_from = getattr(settings, 'TWILIO_PHONE_NUMBER', '')
    if twilio_sid and twilio_token and twilio_from:
        try:
            client = Client(twilio_sid, twilio_token)
            client.messages.create(
                body=message_body,
                from_=twilio_from,
                to=phone_number
            )
            return True, 'twilio', None
        except Exception as e:
            twilio_error = str(e)
    else:
        twilio_error = 'Twilio not configured'

    # ── 3. Email fallback ──
    if fallback_email:
        try:
            send_mail(
                subject=f'Your HMS {purpose} OTP',
                message=(
                    f'Your HMS {purpose} OTP is: {otp}\n\n'
                    f'This OTP is valid for 5 minutes. Do not share it with anyone.\n\n'
                    f'(SMS delivery failed. Fast2SMS: {fast2sms_error} | Twilio: {twilio_error})'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[fallback_email],
                fail_silently=False,
            )
            return True, 'email', None
        except Exception as e:
            return False, 'none', f'All delivery methods failed. Email error: {str(e)}'

    return False, 'none', f'SMS failed. Fast2SMS: {fast2sms_error} | Twilio: {twilio_error}'


def home(request):
    servicedata = Service.objects.all()[:6]
    context = {
        'servicedata': servicedata,
    }
    return render(request, "index.html", context)


def verify_login_otp(request):
    # OTP verification removed — redirect to login
    return redirect('login')



def verify_registration_otp(request):
    # OTP verification removed — redirect to login
    return redirect('login')



def user_login(request):
    servicedata = Service.objects.all()[:6]

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if not user.is_active:
                messages.error(request, 'Your account is pending verification. Please contact support.')
                return redirect('login')
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('login')

    context = {'servicedata': servicedata}
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
        first_name = request.POST.get('firstName', '').strip()
        last_name = request.POST.get('lastName', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        dob = request.POST.get('dob')
        address = request.POST.get('address', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        zip_code = request.POST.get('zip', '').strip()
        university = request.POST.get('university', '').strip()
        enrollmentYear = request.POST.get('enrollmentYear')
        course = request.POST.get('course', '').strip()
        programDuration = request.POST.get('programDuration')
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirmPassword', '')

        # ----- Server-side Validations -----
        errors = []

        if not all([first_name, last_name, email, phone, dob, address, city, state, zip_code, university, enrollmentYear, course, programDuration, username, password]):
            errors.append('All fields are required.')

        if password != confirm_password:
            errors.append('Passwords do not match.')

        if len(password) < 8:
            errors.append('Password must be at least 8 characters long.')

        if not any(c.isdigit() for c in password):
            errors.append('Password must contain at least one number.')

        if not phone.isdigit() or len(phone) != 10:
            errors.append('Phone number must be exactly 10 digits.')

        if User.objects.filter(username=username).exists():
            errors.append('Username already exists. Please choose another.')

        if User.objects.filter(email=email).exists():
            errors.append('Email address is already registered.')

        if Students_data.objects.filter(phone=phone).exists():
            errors.append('Phone number is already registered.')

        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect('login')

        # Directly create user — no OTP verification
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_active=True
        )

        # Create student profile
        student = Students_data(
            user=user,
            phone=phone,
            dob=dob,
            address=address,
            city=city,
            state=state,
            zip=zip_code,
            university=university,
            enrollmentYear=enrollmentYear,
            course=course,
            programDuration=programDuration
        )
        allocate_room_to_student(student)
        student.save()

        login(request, user)
        messages.success(request, f'Welcome, {first_name}! Your account has been created successfully.')
        return redirect('dashboard')


        # Send confirmation email to student
        try:
            send_mail(
                subject='Registration Received — HMS Hostel Management System',
                message='',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=f"""
                <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #0f172a; color: #e2e8f0; border-radius: 16px; overflow: hidden;">
                    <div style="background: linear-gradient(135deg, #6366f1, #8b5cf6); padding: 40px 30px; text-align: center;">
                        <h1 style="margin: 0; font-size: 28px; color: white;">🏨 HMS Portal</h1>
                        <p style="margin: 8px 0 0; opacity: 0.9; color: #e0e7ff;">Hostel Management System</p>
                    </div>
                    <div style="padding: 40px 30px;">
                        <h2 style="color: #a5b4fc; margin-top: 0;">Registration Received!</h2>
                        <p style="color: #cbd5e1; line-height: 1.6;">Dear <strong style="color: #e2e8f0;">{first_name} {last_name}</strong>,</p>
                        <p style="color: #cbd5e1; line-height: 1.6;">
                            Thank you for registering with the HMS Hostel Management System. 
                            Your application has been received and is currently under review.
                        </p>
                        <div style="background: #1e293b; border-left: 4px solid #6366f1; padding: 20px; border-radius: 8px; margin: 24px 0;">
                            <p style="margin: 0; color: #a5b4fc; font-weight: 600;">⏳ What happens next?</p>
                            <p style="margin: 8px 0 0; color: #94a3b8; font-size: 14px;">
                                Our admin team will verify your details within <strong style="color: #e2e8f0;">24 hours</strong>. 
                                Once verified, you will receive another email with your login credentials and room allocation details.
                            </p>
                        </div>
                        <div style="background: #1e293b; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <p style="margin: 0 0 12px; color: #a5b4fc; font-weight: 600;">📋 Your Registration Summary:</p>
                            <table style="width: 100%; font-size: 14px;">
                                <tr><td style="color: #64748b; padding: 4px 0;">Username:</td><td style="color: #e2e8f0;"><strong>{username}</strong></td></tr>
                                <tr><td style="color: #64748b; padding: 4px 0;">Email:</td><td style="color: #e2e8f0;">{email}</td></tr>
                                <tr><td style="color: #64748b; padding: 4px 0;">University:</td><td style="color: #e2e8f0;">{university}</td></tr>
                                <tr><td style="color: #64748b; padding: 4px 0;">Course:</td><td style="color: #e2e8f0;">{course}</td></tr>
                            </table>
                        </div>
                        <p style="color: #64748b; font-size: 13px; margin-top: 30px;">
                            If you did not register for this account, please ignore this email or contact support immediately.
                        </p>
                    </div>
                    <div style="background: #1e293b; padding: 20px 30px; text-align: center; border-top: 1px solid #334155;">
                        <p style="margin: 0; color: #475569; font-size: 13px;">© 2025 HMS — Hostel Management System. All rights reserved.</p>
                    </div>
                </div>
                """,
                fail_silently=True,
            )

            # Notify admin
            send_mail(
                subject=f'New Student Registration — {first_name} {last_name}',
                message=f'New student registered:\n\nName: {first_name} {last_name}\nEmail: {email}\nPhone: {phone}\nUsername: {username}\nUniversity: {university}\nCourse: {course}\n\nPlease verify and activate from Django Admin.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Email error: {e}")

        return redirect('success')

    return render(request, 'login.html')


@login_required
def dashboard(request):
    student = Students_data.objects.filter(user=request.user).first()
    room = student.room if student and student.room else None
    student_data = None
    active_complaints_count = 0
    total_paid = 0
    recent_payments = []
    hostel_status = {
        'days_remaining': 0,
        'state': 'unknown',
        'message': '',
        'color': 'gray'
    }

    if student:
        student_data = {
            "Name": f"{request.user.first_name} {request.user.last_name}",
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
        payments = Payment.objects.filter(student=student, status='paid').order_by('-paid_at')[:5]
        total_paid = sum(p.amount for p in Payment.objects.filter(student=student, status='paid'))
        recent_payments = payments

        # --- Access Days Logic ---
        # 10000 rupees = 30 days of access. No proportional days!
        days_paid_for = (total_paid // 10000) * 30
        
        # Calculate elapsed days since the very first payment, or user join date if no payments
        first_payment = Payment.objects.filter(student=student, status='paid').order_by('paid_at').first()
        if first_payment and first_payment.paid_at:
            start_date = first_payment.paid_at.date()
        else:
            start_date = request.user.date_joined.date()
            
        days_elapsed = (timezone.now().date() - start_date).days
        days_remaining = days_paid_for - days_elapsed
        
        if total_paid < 10000:
            # Haven't paid the first full month yet
            hostel_status = {
                'days': 0,
                'state': 'revoked',
                'message': "No Access",
                'color': 'red'
            }
        else:
            if days_remaining > 0:
                hostel_status = {
                    'days': days_remaining,
                    'state': 'active',
                    'message': f"{days_remaining} Days Left",
                    'color': 'green'
                }
            elif days_remaining >= -15:
                grace_days_left = 15 + days_remaining
                hostel_status = {
                    'days': grace_days_left,
                    'state': 'grace',
                    'message': f"Pay in {grace_days_left} Days",
                    'color': 'yellow'
                }
            else:
                hostel_status = {
                    'days': 0,
                    'state': 'revoked',
                    'message': "Access Revoked",
                    'color': 'red'
                }

    recent_complaints = Complaint.objects.filter(student=student).order_by('-date_submitted')[:3] if student else []

    return render(request, 'dashboard/dashboard.html', {
        'student_data': student_data,
        'active_complaints_count': active_complaints_count,
        'total_paid': total_paid,
        'recent_payments': recent_payments,
        'recent_complaints': recent_complaints,
        'student': student,
        'hostel_status': hostel_status,
    })


@login_required
def update_profile(request):
    if request.method == 'POST':
        student = Students_data.objects.filter(user=request.user).first()
        if not student:
            messages.error(request, 'Student profile not found.')
            return redirect('dashboard')

        # Update user fields
        email = request.POST.get('email', '').strip()

        # Validate email uniqueness
        if email and email != request.user.email:
            if User.objects.filter(email=email).exclude(pk=request.user.pk).exists():
                messages.error(request, 'Email address is already in use by another account.')
                return redirect('profile')

        if email:
            request.user.email = email
        request.user.save()

        # Update student fields
        phone = request.POST.get('phone', '').strip()
        university = request.POST.get('university', '').strip()
        course = request.POST.get('course', '').strip()

        # Phone validation
        if phone and (not phone.isdigit() or len(phone) != 10):
            messages.error(request, 'Phone number must be exactly 10 digits.')
            return redirect('profile')

        if phone and phone != student.phone:
            if Students_data.objects.filter(phone=phone).exclude(pk=student.pk).exists():
                messages.error(request, 'Phone number is already registered to another account.')
                return redirect('profile')
            student.phone = phone
        if university:
            student.university = university
        if course:
            student.course = course

        # Handle profile photo
        if 'profile_photo' in request.FILES:
            student.profile_photo = request.FILES['profile_photo']

        student.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')

    return redirect('profile')


@login_required
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('settings')

        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return redirect('settings')

        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
            return redirect('settings')

        request.user.set_password(new_password)
        request.user.save()
        login(request, request.user)
        messages.success(request, 'Password changed successfully!')
        return redirect('settings')

    return redirect('settings')


@login_required
def complaints(request):
    student = Students_data.objects.filter(user=request.user).first()
    complaint_list = Complaint.objects.filter(student=student).order_by('-date_submitted') if student else []
    
    pending_count = sum(1 for c in complaint_list if c.status == 'pending' or c.status == 'in_progress')
    resolved_count = sum(1 for c in complaint_list if c.status == 'resolved')

    context = {
        'complaints': complaint_list,
        'student': student,
        'pending_count': pending_count,
        'resolved_count': resolved_count,
    }
    return render(request, 'dashboard/complaints.html', context)


@login_required
def payments(request):
    student = Students_data.objects.filter(user=request.user).first()
    payment_list = Payment.objects.filter(student=student).order_by('-created_at') if student else []
    total_paid = sum(p.amount for p in payment_list if p.status == 'paid')
    
    # Calculate days elapsed since first payment to know if they are active
    first_payment = Payment.objects.filter(student=student, status='paid').order_by('paid_at').first()
    if first_payment and first_payment.paid_at:
        start_date = first_payment.paid_at.date()
    else:
        start_date = request.user.date_joined.date()
        
    days_elapsed = (timezone.now().date() - start_date).days
    
    # 10000 total fees for 30 days. No proportional days!
    days_paid_for = (total_paid // 10000) * 30
    days_remaining = days_paid_for - days_elapsed
    
    # Calculate due amount
    if days_remaining > 0:
        due_this_month = 0
    else:
        # If they haven't paid the full 10k block, or if they have but they are expired
        remainder = total_paid % 10000
        due_this_month = 10000 - remainder if remainder != 0 else 10000

    context = {
        'payment_list': payment_list,
        'total_paid': total_paid,
        'student': student,
        'due_this_month': due_this_month,
        'RAZORPAY_KEY_ID': settings.RAZORPAY_KEY_ID,
    }
    return render(request, 'dashboard/payments.html', context)


@login_required
def profile(request):
    student = Students_data.objects.filter(user=request.user).first()
    return render(request, 'dashboard/profile.html', {'student': student})


@login_required
def user_settings(request):
    return render(request, 'dashboard/settings.html')


@login_required
def documents(request):
    Eventdata = Events.objects.all()[:6]
    Noticedata = Notice.objects.all()[:6]
    context = {
        'Noticedata': Noticedata,
        'Eventdata': Eventdata,
    }
    return render(request, 'dashboard/documents.html', context)


def user_logout(request):
    logout(request)
    return redirect('login')


def success(request):
    return render(request, 'successful_registration.html')


# ─────────────────────────── PDF GENERATION ───────────────────────────

class PDF(FPDF):
    def header(self):
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'media', 'logo.jpg')
        if os.path.exists(logo_path):
            self.image(logo_path, x=85, y=10, w=40)
            self.ln(30)
        else:
            self.ln(10)
        self.set_font('Arial', 'B', 18)
        self.set_text_color(99, 102, 241)
        self.cell(0, 10, 'HMS - Hostel Management System', ln=True, align='C')
        self.set_font('Arial', 'B', 14)
        self.set_text_color(30, 30, 30)
        self.cell(0, 8, 'Fee Payment Receipt', ln=True, align='C')
        self.set_draw_color(99, 102, 241)
        self.set_line_width(0.8)
        self.line(10, self.get_y() + 2, 200, self.get_y() + 2)
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Page {self.page_no()} | Generated on {timezone.now().strftime("%d %b %Y, %I:%M %p")} | HMS Portal', align='C')


@login_required
def generate_student_pdf(request):
    payment_id = request.GET.get('payment_id')
    try:
        student = Students_data.objects.filter(user=request.user).first()
        if not student:
            return HttpResponse("Student data not found.", status=404)
        room = student.room if student.room else None
    except Exception:
        return HttpResponse("Error fetching student data.", status=500)

    # Get payment info
    payment = None
    if payment_id:
        payment = Payment.objects.filter(id=payment_id, student=student).first()

    # QR code data
    qr_data = (
        f"HMS Payment Receipt\n"
        f"Name: {request.user.first_name} {request.user.last_name}\n"
        f"Email: {request.user.email}\n"
        f"Username: {request.user.username}\n"
        f"Room: {room.room_number if room else 'Not Allocated'}\n"
    )
    if payment:
        qr_data += f"Amount: Rs.{payment.amount}\nTransaction ID: {payment.razorpay_payment_id}\nDate: {payment.paid_at.strftime('%d %b %Y') if payment.paid_at else 'N/A'}"

    qr_img = qrcode.make(qr_data)
    qr_buffer = io.BytesIO()
    qr_img.save(qr_buffer, 'PNG')
    qr_buffer.seek(0)
    # Write QR to a real temp file so fpdf can load it by path
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False, dir=tempfile.gettempdir()) as qr_temp:
        qr_temp.write(qr_buffer.read())
        qr_path = qr_temp.name

    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)

    row_height = 10

    def safe_str(val):
        if val is None:
            return ""
        # Replace common unsupported characters
        s = str(val).replace('—', '-').replace('–', '-').replace('‘', "'").replace('’', "'").replace('“', '"').replace('”', '"').replace('₹', 'Rs.')
        # Force encoding to latin-1 to avoid any other crashes
        return s.encode('latin-1', 'replace').decode('latin-1')

    def add_section_title(title):
        title = safe_str(title)
        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(99, 102, 241)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 10, f'  {title}', border=0, ln=True, fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", size=11)
        pdf.ln(2)

    def add_row(label, value):
        label = safe_str(label)
        value = safe_str(value)
        pdf.set_font("Arial", 'B', 10)
        pdf.set_fill_color(240, 240, 255)
        pdf.cell(65, row_height, f'  {label}', border=1, fill=True)
        pdf.set_font("Arial", '', 10)
        pdf.set_fill_color(255, 255, 255)
        pdf.cell(125, row_height, f'  {value}', border=1)
        pdf.ln()

    # Personal Information
    add_section_title('Personal Information')
    add_row('Full Name', f"{request.user.first_name} {request.user.last_name}")
    add_row('Username', request.user.username)
    add_row('Email', request.user.email)
    add_row('Phone', student.phone)
    add_row('Date of Birth', str(student.dob))
    add_row('Address', f"{student.address}, {student.city}, {student.state} - {student.zip}")
    pdf.ln(5)

    # Academic Information
    add_section_title('Academic Information')
    add_row('University', student.university)
    add_row('Course', student.course)
    add_row('Enrollment Year', str(student.enrollmentYear))
    add_row('Program Duration', f"{student.programDuration} Year(s)")
    add_row('Room Number', room.room_number if room else 'Not Allocated')
    pdf.ln(5)

    # Payment Information
    add_section_title('Payment Information')
    if payment:
        add_row('Payment Type', payment.get_payment_type_display())
        add_row('Amount Paid', f'Rs. {payment.amount}')
        add_row('Razorpay Order ID', payment.razorpay_order_id or 'N/A')
        add_row('Transaction ID', payment.razorpay_payment_id or 'N/A')
        add_row('Payment Status', payment.status.upper())
        add_row('Payment Date', payment.paid_at.strftime('%d %b %Y, %I:%M %p') if payment.paid_at else 'N/A')
    else:
        add_row('Amount', 'Rs. 5000')
        add_row('Status', 'PAID')
        add_row('Date', timezone.now().strftime('%d %b %Y'))

    # QR Code
    qr_y = pdf.get_y() + 5
    if qr_y + 40 > 270:
        pdf.add_page()
        qr_y = 20
    pdf.image(qr_path, x=160, y=qr_y, w=35)
    pdf.set_font("Arial", 'I', 8)
    pdf.set_text_color(100, 100, 100)
    pdf.set_y(qr_y + 36)
    pdf.cell(0, 5, 'Scan to verify', align='R')

    if os.path.exists(qr_path):
        os.remove(qr_path)

    # Generate PDF in-memory (Vercel has a read-only filesystem)
    pdf_bytes = pdf.output(dest='S').encode('latin-1')

    filename = f"{request.user.username}_{payment_id or 'receipt'}.pdf"

    # Update payment record with a logical path (no actual file written)
    if payment:
        payment.pdf_path = f"receipts/{filename}"
        payment.save()

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response



# ─────────────────────────── MOCK PAYMENT SANDBOX ───────────────────────────

@login_required
def mock_payment(request):
    """
    Sandbox payment endpoint. Accepts any card details,
    creates a Payment record marked as 'paid', and returns the payment ID.
    No real payment gateway is involved.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        amount = data.get('amount', 5000)          # In rupees (not paise)
        payment_type = data.get('payment_type', 'hostel_fee')
        card_name = data.get('card_name', 'Test User')

        student = Students_data.objects.filter(user=request.user).first()
        if not student:
            return JsonResponse({'success': False, 'error': 'Student profile not found'}, status=404)

        # Generate a fake but realistic-looking transaction ID
        import uuid
        fake_order_id  = 'SANDBOX_ORD_' + uuid.uuid4().hex[:12].upper()
        fake_payment_id = 'SANDBOX_PAY_' + uuid.uuid4().hex[:14].upper()

        # Create payment record marked as paid immediately
        payment = Payment.objects.create(
            student=student,
            razorpay_order_id=fake_order_id,
            razorpay_payment_id=fake_payment_id,
            razorpay_signature='SANDBOX_VERIFIED',
            amount=amount,
            payment_type=payment_type,
            status='paid',
            paid_at=timezone.now(),
        )

        # Optional: send confirmation email (fail_silently so it never breaks)
        try:
            send_mail(
                subject='Payment Confirmed (Sandbox) — HMS Hostel',
                message='',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
                html_message=f"""
                <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f8fafc;border-radius:12px;overflow:hidden;border:1px solid #e2e8f0;">
                    <div style="background:#2563eb;padding:28px;text-align:center;">
                        <h1 style="margin:0;color:white;font-size:22px;">✅ Payment Confirmed!</h1>
                        <p style="margin:6px 0 0;color:#bfdbfe;font-size:14px;">Sandbox Mode</p>
                    </div>
                    <div style="padding:28px;">
                        <p style="color:#374151;">Dear <strong>{request.user.first_name or request.user.username}</strong>,</p>
                        <p style="color:#374151;">Your payment of <strong style="color:#16a34a;">₹{payment.amount}</strong> has been recorded.</p>
                        <div style="background:#f1f5f9;border-radius:8px;padding:16px;margin:16px 0;">
                            <table style="width:100%;font-size:14px;color:#374151;">
                                <tr><td style="color:#6b7280;padding:4px 0;width:140px;">Transaction ID</td><td><strong>{fake_payment_id}</strong></td></tr>
                                <tr><td style="color:#6b7280;padding:4px 0;">Amount</td><td><strong>₹{payment.amount}</strong></td></tr>
                                <tr><td style="color:#6b7280;padding:4px 0;">Type</td><td>{payment.get_payment_type_display()}</td></tr>
                                <tr><td style="color:#6b7280;padding:4px 0;">Date</td><td>{payment.paid_at.strftime('%d %b %Y, %I:%M %p')}</td></tr>
                            </table>
                        </div>
                        <p style="color:#6b7280;font-size:13px;">Download your receipt from the HMS portal anytime.</p>
                    </div>
                </div>
                """,
                fail_silently=True,
            )
        except Exception:
            pass

        return JsonResponse({
            'success': True,
            'payment_id': payment.id,
            'transaction_id': fake_payment_id,
            'amount': str(payment.amount),
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ─────────────────────────── GROQ AI CHATBOT ───────────────────────────

@csrf_exempt
def chatbot_ask(request):
    """
    POST /chatbot/ask/
    Body JSON: { "message": "...", "history": [...] }
    Returns JSON: { "reply": "..." }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    user_message = data.get('message', '').strip()
    history = data.get('history', [])  # list of {"role": ..., "content": ...}

    if not user_message:
        return JsonResponse({'error': 'Empty message'}, status=400)

    api_key = settings.GROQ_API_KEY
    if not api_key or api_key == 'your_groq_api_key_here':
        return JsonResponse({'reply': "⚠️ The AI assistant is not yet configured. Please add your Groq API key in the .env file to enable this feature."})

    # Build student context if the user is logged in
    student_context = ""
    if request.user.is_authenticated:
        try:
            student = Students_data.objects.filter(user=request.user).first()
            if student:
                all_payments = Payment.objects.filter(student=student, status='paid')
                total_paid = sum(p.amount for p in all_payments)
                pending_complaints = Complaint.objects.filter(student=student, status='pending').count()
                resolved_complaints = Complaint.objects.filter(student=student, status='resolved').count()
                
                # Calculate access status
                days_paid_for = (total_paid // 10000) * 30
                first_payment = Payment.objects.filter(student=student, status='paid').order_by('paid_at').first()
                if first_payment and first_payment.paid_at:
                    start_date = first_payment.paid_at.date()
                    days_elapsed = (timezone.now().date() - start_date).days
                    days_remaining = days_paid_for - days_elapsed
                    if total_paid < 10000:
                        access_status = "No Access (full ₹10,000 not paid yet)"
                    elif days_remaining > 0:
                        access_status = f"Active — {days_remaining} days remaining"
                    elif days_remaining >= -15:
                        access_status = f"Grace period — {15 + days_remaining} days to pay"
                    else:
                        access_status = "Access Revoked"
                else:
                    access_status = "No Access (no payments made)"

                room = student.room.room_number if student.room else "Not Allocated"
                due = 10000 - (total_paid % 10000) if total_paid % 10000 != 0 else (0 if total_paid > 0 and days_remaining > 0 else 10000)
                
                student_context = f"""
The student you are helping has the following account details:
- Name: {request.user.get_full_name() or request.user.username}
- Room: {room}
- University: {student.university or 'N/A'}
- Course: {student.course or 'N/A'}
- Total Fees Paid: ₹{total_paid}
- Due This Month: ₹{due}
- Hostel Access Status: {access_status}
- Pending Complaints: {pending_complaints}
- Resolved Complaints: {resolved_complaints}
"""
        except Exception:
            student_context = ""

    system_prompt = f"""You are HMS Assistant, a friendly and knowledgeable AI chatbot for the HMS (Hostel Management System) portal.

Your role is to help students with:
- Questions about their hostel fees, payments, and access status
- Information about complaints and maintenance requests
- General hostel rules, facilities, and policies
- Navigating the HMS portal
- Any other hostel-related queries

HMS Fee Structure:
- Total monthly fee: ₹10,000 (must be paid in full to get access)
  - Hostel Fee: ₹5,000
  - Mess Fee: ₹3,000  
  - Maintenance: ₹2,000
- Full payment gives 30 days of hostel access
- After 30 days, there is a 15-day grace period to renew
- No access is given until the full ₹10,000 is paid

{student_context}

Be concise, warm, and helpful. Use emojis occasionally to be friendly. If you don't know something specific about the hostel's internal policies, say so and suggest they contact the hostel administration."""

    # Build the messages list for Groq
    messages = [{"role": "system", "content": system_prompt}]
    # Add conversation history (last 10 turns to stay within token limits)
    for msg in history[-10:]:
        if msg.get('role') in ('user', 'assistant') and msg.get('content'):
            messages.append({"role": msg['role'], "content": msg['content']})
    messages.append({"role": "user", "content": user_message})

    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=512,
            temperature=0.7,
        )
        reply = completion.choices[0].message.content
        return JsonResponse({'reply': reply})
    except Exception as e:
        return JsonResponse({'reply': f"⚠️ AI Error: {str(e)}"})