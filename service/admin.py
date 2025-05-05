from django.contrib import admin
from service.models import Students_data, Room

@admin.register(Students_data)
class StudentsDataAdmin(admin.ModelAdmin):
    list_display = (
        'get_username', 'get_email', 'phone', 'dob', 'address', 'city',
        'state', 'zip', 'university', 'enrollmentYear', 'course', 'programDuration', 'room', 'is_active'
    )
    search_fields = ('user__username', 'user__email', 'phone', 'university', 'course')

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'floor_number', 'capacity', 'available_slots')


admin.site.site_header = "HMS Admin"
