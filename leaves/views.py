from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone

from accounts.decorators import employee_required, hr_required
from .models import LeaveRequest
from .forms import LeaveApplyForm, LeaveActionForm
from employees.models import Employee
from notifications.models import Notification


@employee_required
def leave_apply_view(request):
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        messages.error(request, "No associated employee record found.")
        return redirect('login_redirect')

    if request.method == 'POST':
        form = LeaveApplyForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.employee = employee
            leave.status = 'PENDING'
            leave.save()
            messages.success(request, f"Leave application ({leave.total_days} days) submitted for review.")
            return redirect('my_leaves')
        else:
            messages.error(request, "Please address the errors highlighted below.")
    else:
        form = LeaveApplyForm()

    return render(request, 'leaves/leave_apply.html', {'form': form})


@employee_required
def my_leaves_view(request):
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        messages.error(request, "No associated employee record found.")
        return redirect('login_redirect')

    leaves = LeaveRequest.objects.filter(employee=employee).order_by('-applied_at')
    
    # Counts
    pending_count = leaves.filter(status='PENDING').count()
    approved_count = leaves.filter(status='APPROVED').count()
    rejected_count = leaves.filter(status='REJECTED').count()

    paginator = Paginator(leaves, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
    }
    return render(request, 'leaves/my_leaves.html', context)


@hr_required
def leave_list_view(request):
    queryset = LeaveRequest.objects.select_related('employee__user', 'employee__department').order_by('-applied_at')

    # Filters
    status = request.GET.get('status', '')
    if status:
        queryset = queryset.filter(status=status)

    leave_type = request.GET.get('leave_type', '')
    if leave_type:
        queryset = queryset.filter(leave_type=leave_type)

    paginator = Paginator(queryset, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'selected_status': status,
        'selected_type': leave_type,
    }
    return render(request, 'leaves/leave_list.html', context)


@hr_required
def leave_action_view(request, pk):
    leave = get_object_or_404(LeaveRequest.objects.select_related('employee__user'), pk=pk)

    if request.method == 'POST':
        form = LeaveActionForm(request.POST, instance=leave)
        if form.is_valid():
            updated_leave = form.save(commit=False)
            updated_leave.approved_by = request.user
            updated_leave.action_taken_at = timezone.now()
            updated_leave.save()

            # Automatic Notification dispatch to applicant
            Notification.objects.create(
                recipient=leave.employee.user,
                title=f"Leave Request {updated_leave.status}",
                message=f"Your {updated_leave.get_leave_type_display()} request ({updated_leave.start_date} to {updated_leave.end_date}) was marked {updated_leave.status}.",
                notification_type='LEAVE',
                link='/leaves/my/'
            )

            messages.success(request, f"Leave decision for {leave.employee.full_name} saved successfully.")
            return redirect('leave_list')
        else:
            messages.error(request, "Please rectify the input errors.")
    else:
        form = LeaveActionForm(instance=leave)

    return render(request, 'leaves/leave_action.html', {'form': form, 'leave': leave})