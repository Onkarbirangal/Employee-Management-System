from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.utils import timezone

from accounts.decorators import admin_required, hr_required, employee_required
from .models import Employee
from .forms import EmployeeCreateForm, EmployeeUpdateForm
from departments.models import Department, Designation
from attendance.models import Attendance
from leaves.models import LeaveRequest
from payroll.models import SalaryRecord
from notifications.models import Notification


# --- DASHBOARD VIEWS (From Step 16) ---
@admin_required
def admin_dashboard_view(request):
    today = timezone.now().date()
    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(status='ACTIVE').count()
    total_departments = Department.objects.count()

    present_today = Attendance.objects.filter(date=today, status='PRESENT').count()
    absent_today = Attendance.objects.filter(date=today, status='ABSENT').count()
    half_day_today = Attendance.objects.filter(date=today, status='HALF_DAY').count()

    pending_leaves = LeaveRequest.objects.filter(status='PENDING').count()
    approved_leaves = LeaveRequest.objects.filter(status='APPROVED').count()

    monthly_payroll_total = SalaryRecord.objects.filter(
        month=today.month,
        year=today.year
    ).aggregate(total=Sum('net_salary'))['total'] or 0.00

    recent_employees = Employee.objects.select_related('user', 'department', 'designation').order_by('-created_at')[:5]
    recent_leaves = LeaveRequest.objects.select_related('employee__user').filter(status='PENDING').order_by('-applied_at')[:5]

    context = {
        'total_employees': total_employees,
        'active_employees': active_employees,
        'total_departments': total_departments,
        'present_today': present_today,
        'absent_today': absent_today,
        'half_day_today': half_day_today,
        'pending_leaves': pending_leaves,
        'approved_leaves': approved_leaves,
        'monthly_payroll_total': monthly_payroll_total,
        'recent_employees': recent_employees,
        'recent_leaves': recent_leaves,
    }
    return render(request, 'employees/admin_dashboard.html', context)


@hr_required
def hr_dashboard_view(request):
    today = timezone.now().date()
    total_employees = Employee.objects.filter(status='ACTIVE').count()
    total_departments = Department.objects.count()
    present_today = Attendance.objects.filter(date=today, status='PRESENT').count()
    absent_today = Attendance.objects.filter(date=today, status='ABSENT').count()
    pending_leaves = LeaveRequest.objects.filter(status='PENDING').count()

    recent_leaves = LeaveRequest.objects.select_related('employee__user').filter(status='PENDING').order_by('-applied_at')[:5]
    recent_employees = Employee.objects.select_related('user', 'department', 'designation').order_by('-created_at')[:5]

    context = {
        'total_employees': total_employees,
        'total_departments': total_departments,
        'present_today': present_today,
        'absent_today': absent_today,
        'pending_leaves': pending_leaves,
        'recent_leaves': recent_leaves,
        'recent_employees': recent_employees,
    }
    return render(request, 'employees/hr_dashboard.html', context)


@employee_required
def employee_dashboard_view(request):
    today = timezone.now().date()
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        return redirect('admin_dashboard')

    today_attendance = Attendance.objects.filter(employee=employee, date=today).first()
    my_pending_leaves = LeaveRequest.objects.filter(employee=employee, status='PENDING').count()
    my_approved_leaves = LeaveRequest.objects.filter(employee=employee, status='APPROVED').count()
    latest_salary = SalaryRecord.objects.filter(employee=employee).order_by('-year', '-month').first()
    recent_leaves = LeaveRequest.objects.filter(employee=employee).order_by('-applied_at')[:4]
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]

    context = {
        'employee': employee,
        'today_attendance': today_attendance,
        'my_pending_leaves': my_pending_leaves,
        'my_approved_leaves': my_approved_leaves,
        'latest_salary': latest_salary,
        'recent_leaves': recent_leaves,
        'notifications': notifications,
    }
    return render(request, 'employees/employee_dashboard.html', context)


# --- EMPLOYEE CRUD, SEARCH & FILTER VIEWS ---
@hr_required
def employee_list_view(request):
    queryset = Employee.objects.select_related('user', 'department', 'designation').order_by('employee_id')

    # 1. Search Query (Q Objects)
    query = request.GET.get('q', '').strip()
    if query:
        queryset = queryset.filter(
            Q(employee_id__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__email__icontains=query) |
            Q(phone__icontains=query)
        )

    # 2. Filters
    dept_id = request.GET.get('department')
    if dept_id:
        queryset = queryset.filter(department_id=dept_id)

    role = request.GET.get('role')
    if role:
        queryset = queryset.filter(role=role)

    status = request.GET.get('status')
    if status:
        queryset = queryset.filter(status=status)

    # 3. Pagination (10 per page)
    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    departments = Department.objects.all()

    return render(request, 'employees/employee_list.html', {
        'page_obj': page_obj,
        'departments': departments,
        'query': query,
        'selected_dept': dept_id,
        'selected_role': role,
        'selected_status': status,
    })


@hr_required
def employee_create_view(request):
    if request.method == 'POST':
        form = EmployeeCreateForm(request.POST, request.FILES)
        if form.is_valid():
            # 1. Create Django Auth User
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name']
            )

            # 2. Prevent non-admin HR from creating Superusers/Admins
            employee = form.save(commit=False)
            employee.user = user
            if not request.user.is_superuser and form.cleaned_data['role'] == 'ADMIN':
                employee.role = 'EMPLOYEE'

            employee.save()
            messages.success(request, f"Employee {employee.full_name} created successfully!")
            return redirect('employee_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = EmployeeCreateForm()

    return render(request, 'employees/employee_form.html', {
        'form': form,
        'title': 'Add New Employee',
        'btn_text': 'Save Employee',
    })


@employee_required
def employee_detail_view(request, pk):
    employee = get_object_or_404(Employee.objects.select_related('user', 'department', 'designation'), pk=pk)

    # Security check: Non-HR/Admin users can ONLY view their own profile
    if not (request.user.is_superuser or request.user.employee.role in ['ADMIN', 'HR']):
        if request.user.employee.pk != employee.pk:
            messages.error(request, "You do not have permission to view other employee profiles.")
            return redirect('employee_dashboard')

    return render(request, 'employees/employee_detail.html', {'employee': employee})


@hr_required
def employee_update_view(request, pk):
    employee = get_object_or_404(Employee, pk=pk)

    # Security: Only superusers/admins can edit another Admin's profile
    if employee.role == 'ADMIN' and not (request.user.is_superuser or request.user.employee.role == 'ADMIN'):
        messages.error(request, "HR Managers cannot modify Administrator profiles.")
        return redirect('employee_list')

    if request.method == 'POST':
        form = EmployeeUpdateForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            # Update associated User fields
            user = employee.user
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()

            form.save()
            messages.success(request, f"Profile for {employee.full_name} updated successfully!")
            return redirect('employee_detail', pk=employee.pk)
        else:
            messages.error(request, "Please correct the highlighted errors.")
    else:
        form = EmployeeUpdateForm(instance=employee)

    return render(request, 'employees/employee_form.html', {
        'form': form,
        'title': f'Edit Employee: {employee.full_name}',
        'btn_text': 'Update Employee',
    })


@admin_required
def employee_delete_view(request, pk):
    employee = get_object_or_404(Employee, pk=pk)

    # Security: Cannot delete superuser
    if employee.user.is_superuser:
        messages.error(request, "Cannot delete a primary superuser account.")
        return redirect('employee_list')

    if request.method == 'POST':
        name = employee.full_name
        # Deleting the user automatically deletes the Employee profile via CASCADE
        employee.user.delete()
        messages.success(request, f"Employee {name} was permanently removed.")
        return redirect('employee_list')

    return render(request, 'employees/employee_confirm_delete.html', {'employee': employee})


@employee_required
def my_profile_view(request):
    """Convenience redirect to the logged-in user's own profile detail page."""
    try:
        return redirect('employee_detail', pk=request.user.employee.pk)
    except Employee.DoesNotExist:
        messages.error(request, "No employee record associated with your account.")
        return redirect('login_redirect')