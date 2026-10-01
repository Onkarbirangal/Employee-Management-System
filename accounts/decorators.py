from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages


def role_required(allowed_roles=None):
    """
    Decorator factory that enforces role-based access control.
    allowed_roles should be a list or tuple of role strings, e.g. ['ADMIN', 'HR'].
    """
    if allowed_roles is None:
        allowed_roles = []

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # 1. Ensure user is logged in
            if not request.user.is_authenticated:
                return redirect('login')

            # 2. Unconditional grant for Django superusers
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # 3. Check for associated Employee profile
            try:
                employee = request.user.employee
            except Exception:
                messages.error(request, "No employee record associated with this account.")
                return redirect('login')

            # 4. Check account status
            if employee.status != 'ACTIVE':
                messages.error(request, "Your employee account is inactive. Please contact HR.")
                return redirect('login')

            # 5. Check role authorization
            if employee.role in allowed_roles:
                return view_func(request, *args, **kwargs)

            # 6. Raise 403 Forbidden if not authorized
            raise PermissionDenied

        return _wrapped_view
    return decorator


def admin_required(view_func):
    """Strictly restricts access to Admin role and Superusers."""
    return role_required(['ADMIN'])(view_func)


def hr_required(view_func):
    """Allows access to HR / Managers and Admins."""
    return role_required(['ADMIN', 'HR'])(view_func)


def employee_required(view_func):
    """Allows access to all active employees (Employee, HR, Admin)."""
    return role_required(['ADMIN', 'HR', 'EMPLOYEE'])(view_func)