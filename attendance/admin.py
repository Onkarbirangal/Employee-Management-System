from django.contrib import admin
from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'check_in', 'check_out', 'status', 'created_at')
    list_filter = ('status', 'date', 'employee__department')
    search_fields = (
        'employee__employee_id',
        'employee__user__first_name',
        'employee__user__last_name',
        'remarks',
    )
    date_hierarchy = 'date'
    ordering = ('-date', 'employee')