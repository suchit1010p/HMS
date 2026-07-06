from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from HMS import views
from .views import user_login, generate_student_pdf
from services.views import submit_complaint

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home),
    path('login/', user_login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.RegisterNewStudent, name='register'),
    path('success/', views.success, name='success'),
    path('fees-receipt/', generate_student_pdf, name='student_pdf'),
    path('logout/', views.user_logout, name='logout'),
    path('save/', views.saveEnquiry, name="save"),

    # Dashboard pages
    path('complaints/', views.complaints, name='complaints'),
    path('payments/', views.payments, name='payments'),
    path('profile/', views.profile, name='profile'),
    path('documents/', views.documents, name='documents'),
    path('settings/', views.user_settings, name='settings'),

    # Forms/Actions
    path('submit_complaint/', submit_complaint, name='submit_complaint'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('change_password/', views.change_password, name='change_password'),

    # Mock Payment Sandbox
    path('mock-payment/', views.mock_payment, name='mock_payment'),

    # OTP Verification
    path('verify-login-otp/', views.verify_login_otp, name='verify_login_otp'),
    path('verify-registration-otp/', views.verify_registration_otp, name='verify_registration_otp'),

    # Groq AI Chatbot
    path('chatbot/ask/', views.chatbot_ask, name='chatbot_ask'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
