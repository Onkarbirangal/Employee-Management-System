from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Sum, Q

from accounts.decorators import hr_required, employee_required
from .models import SalaryRecord
from .forms import SalaryRecordForm
from employees.models import Employee
from notifications.models import Notification


@hr_required
def salary_list_view(request):
    queryset = SalaryRecord.objects.select_related('employee__user', 'employee__department').order_by('-year', '-month')

    query = request.GET.get('q', '').strip()
    if query:
        queryset = queryset.filter(
            Q(employee__employee_id__icontains=query) |
            Q(employee__user__first_name__icontains=query) |
            Q(employee__user__last_name__icontains=query)
        )

    month = request.GET.get('month', '')
    if month:
        queryset = queryset.filter(month=month)

    year = request.GET.get('year', '')
    if year:
        queryset = queryset.filter(year=year)

    status = request.GET.get('status', '')
    if status:
        queryset = queryset.filter(payment_status=status)

    # Aggregates for filter view
    total_disbursed = queryset.aggregate(total=Sum('net_salary'))['total'] or 0.00

    paginator = Paginator(queryset, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
        'selected_month': month,
        'selected_year': year,
        'selected_status': status,
        'total_disbursed': total_disbursed,
    }
    return render(request, 'payroll/salary_list.html', context)


@hr_required
def salary_create_view(request):
    if request.method == 'POST':
        form = SalaryRecordForm(request.POST)
        if form.is_valid():
            salary = form.save()

            # Automatic notification to employee
            Notification.objects.create(
                recipient=salary.employee.user,
                title="Salary Slip Generated",
                message=f"Your payslip for {salary.month}/{salary.year} (Net: ₹{salary.net_salary}) is available.",
                notification_type='PAYROLL',
                link=f'/payroll/{salary.pk}/'
            )

            messages.success(request, f"Payslip for {salary.employee.full_name} generated successfully!")
            return redirect('salary_list')
        else:
            messages.error(request, "Please address the errors highlighted below.")
    else:
        today = timezone.now().date()
        form = SalaryRecordForm(initial={
            'month': today.month,
            'year': today.year,
            'allowance': 0.00,
            'bonus': 0.00,
            'deduction': 0.00,
            'payment_status': 'PAID',
            'payment_date': today,
        })

    return render(request, 'payroll/salary_form.html', {
        'form': form,
        'title': 'Generate Monthly Payslip',
        'btn_text': 'Generate Slip',
    })


@hr_required
def salary_update_view(request, pk):
    salary = get_object_or_404(SalaryRecord, pk=pk)
    if request.method == 'POST':
        form = SalaryRecordForm(request.POST, instance=salary)
        if form.is_valid():
            salary = form.save()
            messages.success(request, f"Salary record #{salary.pk} updated successfully.")
            return redirect('salary_detail', pk=salary.pk)
        else:
            messages.error(request, "Please rectify the input errors.")
    else:
        form = SalaryRecordForm(instance=salary)

    return render(request, 'payroll/salary_form.html', {
        'form': form,
        'title': f'Edit Salary Record #{salary.pk} ({salary.employee.full_name})',
        'btn_text': 'Update Record',
    })


@employee_required
def salary_detail_view(request, pk):
    salary = get_object_or_404(
        SalaryRecord.objects.select_related('employee__user', 'employee__department', 'employee__designation'),
        pk=pk
    )

    # Privacy Protection: Check ownership if not HR or Admin
    if not (request.user.is_superuser or request.user.employee.role in ['ADMIN', 'HR']):
        if request.user.employee.pk != salary.employee.pk:
            messages.error(request, "You do not have permission to view other employees' salary slips.")
            return redirect('my_salary')

    return render(request, 'payroll/salary_detail.html', {'salary': salary})


@employee_required
def my_salary_view(request):
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        messages.error(request, "No associated employee record found.")
        return redirect('login_redirect')

    salaries = SalaryRecord.objects.filter(employee=employee).order_by('-year', '-month')

    paginator = Paginator(salaries, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'payroll/my_salary.html', {
        'employee': employee,
        'page_obj': page_obj,
    })