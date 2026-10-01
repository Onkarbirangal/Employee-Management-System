from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import uuid

from .forms import UserLoginForm, UserRegisterForm, CustomPasswordChangeForm
from employees.models import Employee


def user_login_view(request):
    if request.user.is_authenticated:
        return redirect('login_redirect')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
            return redirect('login_redirect')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def user_register_view(request):
    if request.user.is_authenticated:
        return redirect('login_redirect')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            # 1. Create the base User
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # 2. Auto-generate clean Employee ID (e.g., EMP-XXXXXX)
            generated_emp_id = f"EMP-{uuid.uuid4().hex[:6].upper()}"

            # 3. Create associated Employee profile with default role EMPLOYEE
            Employee.objects.create(
                user=user,
                employee_id=generated_emp_id,
                role='EMPLOYEE',
                status='ACTIVE'
            )

            messages.success(request, "Account created successfully! Please login.")
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def user_logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


@login_required
def login_redirect_view(request):
    """
    Central dispatcher: evaluates user credentials and directs
    the user strictly to their corresponding role dashboard.
    """
    # 1. Django Superuser gets unconditional Admin access
    if request.user.is_superuser:
        return redirect('admin_dashboard')

    # 2. Check Employee profile role
    try:
        employee_profile = request.user.employee
        if employee_profile.role == 'ADMIN':
            return redirect('admin_dashboard')
        elif employee_profile.role == 'HR':
            return redirect('hr_dashboard')
        else:
            return redirect('employee_dashboard')
    except Employee.DoesNotExist:
        # Fallback if a superuser or staff lacks an Employee profile
        if request.user.is_staff:
            return redirect('admin_dashboard')
        messages.error(request, "No employee record associated with this account.")
        return redirect('login')


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep user logged in after password change
            messages.success(request, "Your password was successfully updated!")
            return redirect('login_redirect')
        else:
            messages.error(request, "Please correct the highlighted errors.")
    else:
        form = CustomPasswordChangeForm(user=request.user)

    return render(request, 'accounts/change_password.html', {'form': form})