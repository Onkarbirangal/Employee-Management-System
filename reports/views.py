from django.shortcuts import render
from django.db.models import Count, Sum
from django.utils import timezone
from accounts.decorators import hr_required
from employees.models import Employee
from departments.models import Department
from attendance.models import Attendance
from leaves.models import LeaveRequest
from payroll.models import SalaryRecord


@hr_required
def reports_hub_view(request):
    today = timezone.now().date()
    current_month = today.month
    current_year = today.year

    # 1. Department Workforce Allocation
    dept_distribution = Department.objects.annotate(
        staff_count=Count('employees')
    ).order_by('-staff_count')

    # 2. Today's Organization Attendance Breakdown
    total_active_staff = Employee.objects.filter(status='ACTIVE').count()
    present_today = Attendance.objects.filter(date=today, status='PRESENT').count()
    absent_today = Attendance.objects.filter(date=today, status='ABSENT').count()
    attendance_rate = round((present_today / total_active_staff * 100), 1) if total_active_staff > 0 else 0

    # 3. Leave Distribution by Type
    leave_stats = LeaveRequest.objects.values('leave_type').annotate(
        total_requests=Count('id')
    ).order_by('-total_requests')

    # 4. Departmental Payroll Cost (Current Year)
    dept_payroll = Department.objects.annotate(
        total_payroll=Sum('employees__salary_records__net_salary')
    ).filter(total_payroll__gt=0).order_by('-total_payroll')

    total_yearly_payroll = SalaryRecord.objects.filter(
        year=current_year
    ).aggregate(total=Sum('net_salary'))['total'] or 0.00

    context = {
        'dept_distribution': dept_distribution,
        'total_active_staff': total_active_staff,
        'present_today': present_today,
        'absent_today': absent_today,
        'attendance_rate': attendance_rate,
        'leave_stats': leave_stats,
        'dept_payroll': dept_payroll,
        'total_yearly_payroll': total_yearly_payroll,
        'current_year': current_year,
    }
    return render(request, 'reports/reports_hub.html', context)