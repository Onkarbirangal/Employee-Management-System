from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q

from accounts.decorators import hr_required, employee_required
from .models import Attendance
from .forms import AttendanceForm
from departments.models import Department
from employees.models import Employee


@hr_required
def attendance_list_view(request):
    queryset = Attendance.objects.select_related('employee__user', 'employee__department').order_by('-date', 'employee__employee_id')

    # 1. Search Query
    query = request.GET.get('q', '').strip()
    if query:
        queryset = queryset.filter(
            Q(employee__employee_id__icontains=query) |
            Q(employee__user__first_name__icontains=query) |
            Q(employee__user__last_name__icontains=query)
        )

    # 2. Filters
    filter_date = request.GET.get('date', '')
    if filter_date:
        queryset = queryset.filter(date=filter_date)

    filter_status = request.GET.get('status', '')
    if filter_status:
        queryset = queryset.filter(status=filter_status)

    filter_dept = request.GET.get('department', '')
    if filter_dept:
        queryset = queryset.filter(employee__department_id=filter_dept)

    # 3. Pagination (15 per page)
    paginator = Paginator(queryset, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    departments = Department.objects.all()

    context = {
        'page_obj': page_obj,
        'departments': departments,
        'query': query,
        'filter_date': filter_date,
        'filter_status': filter_status,
        'filter_dept': filter_dept,
    }
    return render(request, 'attendance/attendance_list.html', context)


@hr_required
def attendance_create_view(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            attendance = form.save()
            messages.success(request, f"Attendance recorded for {attendance.employee.full_name}.")
            return redirect('attendance_list')
        else:
            messages.error(request, "Please correct the highlighted errors.")
    else:
        form = AttendanceForm(initial={'date': timezone.now().date(), 'status': 'PRESENT'})

    return render(request, 'attendance/attendance_form.html', {
        'form': form,
        'title': 'Record Employee Attendance',
        'btn_text': 'Save Record',
    })


@hr_required
def attendance_update_view(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    if request.method == 'POST':
        form = AttendanceForm(request.POST, instance=attendance)
        if form.is_valid():
            form.save()
            messages.success(request, f"Attendance for {attendance.employee.full_name} updated successfully.")
            return redirect('attendance_list')
        else:
            messages.error(request, "Please correct the highlighted errors.")
    else:
        form = AttendanceForm(instance=attendance)

    return render(request, 'attendance/attendance_form.html', {
        'form': form,
        'title': f'Edit Attendance: {attendance.employee.full_name} ({attendance.date})',
        'btn_text': 'Update Attendance',
    })


@employee_required
def my_attendance_view(request):
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        messages.error(request, "No employee record found.")
        return redirect('login_redirect')

    attendances = Attendance.objects.filter(employee=employee).order_by('-date')

    # Date filter
    month = request.GET.get('month')
    year = request.GET.get('year')
    if month and year:
        attendances = attendances.filter(date__month=month, date__year=year)

    paginator = Paginator(attendances, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Check today's status
    today = timezone.now().date()
    today_record = Attendance.objects.filter(employee=employee, date=today).first()

    context = {
        'employee': employee,
        'page_obj': page_obj,
        'today_record': today_record,
        'today': today,
    }
    return render(request, 'attendance/my_attendance.html', context)


@employee_required
def clock_in_view(request):
    if request.method == 'POST':
        employee = request.user.employee
        today = timezone.now().date()
        current_time = timezone.localtime().time()

        record, created = Attendance.objects.get_or_create(
            employee=employee,
            date=today,
            defaults={
                'check_in': current_time,
                'status': 'PRESENT'
            }
        )

        if created:
            messages.success(request, f"Clocked in successfully at {current_time.strftime('%I:%M %p')}!")
        else:
            messages.warning(request, "You have already clocked in for today.")

    return redirect('my_attendance')


@employee_required
def clock_out_view(request):
    if request.method == 'POST':
        employee = request.user.employee
        today = timezone.now().date()
        current_time = timezone.localtime().time()

        record = Attendance.objects.filter(employee=employee, date=today).first()
        if record:
            if not record.check_out:
                record.check_out = current_time
                record.save()
                messages.success(request, f"Clocked out successfully at {current_time.strftime('%I:%M %p')}!")
            else:
                messages.info(request, "You have already clocked out for today.")
        else:
            messages.error(request, "Cannot clock out without clocking in first.")

    return redirect('my_attendance')