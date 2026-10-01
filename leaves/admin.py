from django.contrib import admin
from .models import LeaveRequest


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = (
        'employee',
        'leave_type',
        'start_date',
        'end_date',
        'total_days',
        'status',
        'applied_at',
        'approved_by',
    )
    list_filter = ('status', 'leave_type', 'start_date')
    search_fields = (
        'employee__employee_id',
        'employee__user__first_name',
        'employee__user__last_name',
        'reason',
    )
    ordering = ('-applied_at',)