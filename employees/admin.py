from django.contrib import admin
from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        'employee_id',
        'get_full_name',
        'get_email',
        'department',
        'designation',
        'role',
        'status',
        'joining_date',
    )
    list_filter = ('role', 'status', 'department', 'gender')
    search_fields = (
        'employee_id',
        'user__username',
        'user__first_name',
        'user__last_name',
        'user__email',
        'phone',
    )
    ordering = ('employee_id',)

    @admin.display(description='Full Name')
    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

    @admin.display(description='Email')
    def get_email(self, obj):
        return obj.user.email