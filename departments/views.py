from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count

from accounts.decorators import hr_required, admin_required
from .models import Department, Designation
from .forms import DepartmentForm, DesignationForm


@hr_required
def department_list_view(request):
    # Annotate employee count per department
    departments = Department.objects.annotate(
        total_staff=Count('employees')
    ).prefetch_related('designations').order_by('name')

    designation_form = DesignationForm()
    return render(request, 'departments/department_list.html', {
        'departments': departments,
        'designation_form': designation_form,
    })


@hr_required
def department_create_view(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            dept = form.save()
            messages.success(request, f"Department '{dept.name}' created successfully!")
            return redirect('department_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DepartmentForm()

    return render(request, 'departments/department_form.html', {
        'form': form,
        'title': 'Create New Department',
        'btn_text': 'Create Department',
    })


@hr_required
def department_update_view(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            dept = form.save()
            messages.success(request, f"Department '{dept.name}' updated successfully!")
            return redirect('department_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DepartmentForm(instance=department)

    return render(request, 'departments/department_form.html', {
        'form': form,
        'title': f'Edit Department: {department.name}',
        'btn_text': 'Update Changes',
    })


@admin_required
def department_delete_view(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        name = department.name
        department.delete()
        messages.success(request, f"Department '{name}' was deleted.")
        return redirect('department_list')

    return render(request, 'departments/department_confirm_delete.html', {
        'department': department
    })


@hr_required
def designation_create_view(request):
    if request.method == 'POST':
        form = DesignationForm(request.POST)
        if form.is_valid():
            designation = form.save()
            messages.success(request, f"Designation '{designation.title}' added to {designation.department.name}!")
        else:
            messages.error(request, "Failed to create designation. Title must be unique within the department.")
    return redirect('department_list')