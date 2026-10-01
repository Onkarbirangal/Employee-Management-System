from django.contrib import admin
from .models import SalaryRecord


@admin.register(SalaryRecord)
class SalaryRecordAdmin(admin.ModelAdmin):
    list_display = (
        'employee',
        'month',
        'year',
        'basic_salary',
        'allowance',
        'bonus',
        'deduction',
        'net_salary',
        'payment_status',
        'payment_date',
    )
    list_filter = ('payment_status', 'year', 'month', 'employee__department')
    search_fields = (
        'employee__employee_id',
        'employee__user__first_name',
        'employee__user__last_name',
    )
    readonly_fields = ('net_salary', 'created_at', 'updated_at')
    ordering = ('-year', '-month')