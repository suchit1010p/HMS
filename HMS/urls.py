"""
URL configuration for HMS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from HMS import views
from .views import user_login
from .views import generate_student_pdf
from services.views import submit_complaint

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home),
    path('login/', user_login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.RegisterNewStudent, name='register'),
    path('success/', views.success, name='success'),
    path('fees-receipt/', generate_student_pdf, name='student_pdf'),
    path('logout/', views.user_logout, name='logout'),
    path('save/', views.saveEnquiry, name="save"),
    
    # after visiting the dashbord
    path('complaints/', views.complaints, name='complaints'),
    path('payments/', views.payments, name='payments'),
    path('profile/', views.profile, name='profile'),
    path('documents/', views.documents, name='documents'),
    path('settings/', views.settings, name='settings'),
    path('submit_complaint/', submit_complaint, name='submit_complaint'),
    
]

