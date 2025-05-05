from django.contrib import admin
from service.models import Students_data  # Ensure this path is correct
from services.models import Service, Complaint  # Adjust if needed

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('img_location', 'icon_name', 'ser_name', 'description')
    search_fields = ('icon_name', 'ser_name')

class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_student_name', 'get_complaint_type', 'room_number', 'status', 'date_submitted')
    list_filter = ('status', 'complaint_type', 'date_submitted')
    search_fields = ('complaint_type', 'room_number', 'student__user__username', 'description')
    ordering = ('-date_submitted',)

    def get_student_name(self, obj):
        return obj.student.user.username
    get_student_name.short_description = 'Student'

    def get_complaint_type(self, obj):
        return obj.get_complaint_type_display()
    get_complaint_type.short_description = 'Complaint Type'

admin.site.register(Service, ServiceAdmin)
admin.site.register(Complaint, ComplaintAdmin)


