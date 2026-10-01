"""
URL configuration for employee_management project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Built-in Django administrative panel
    path('admin/', admin.site.urls),

    # Application routes will be plugged in as we build each module:
    path('', include('accounts.urls')),
    path('', include('employees.urls')),
    path('departments/', include('departments.urls')),
    path('attendance/', include('attendance.urls')),
    path('leaves/', include('leaves.urls')),
    path('payroll/', include('payroll.urls')),  # Payroll module
    path('notifications/', include('notifications.urls')),  # Notifications module
    path('reports/', include('reports.urls')),              # Reports module
]

# Serve media files in development environment when DEBUG is True
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)