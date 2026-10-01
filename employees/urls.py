from django.urls import path
from . import views

urlpatterns = [
    # Dashboards
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('hr-dashboard/', views.hr_dashboard_view, name='hr_dashboard'),
    path('employee-dashboard/', views.employee_dashboard_view, name='employee_dashboard'),

    # Profile shortcut
    path('profile/', views.my_profile_view, name='my_profile'),

    # Employee CRUD
    path('employees/', views.employee_list_view, name='employee_list'),
    path('employees/add/', views.employee_create_view, name='employee_add'),
    path('employees/<int:pk>/', views.employee_detail_view, name='employee_detail'),
    path('employees/<int:pk>/edit/', views.employee_update_view, name='employee_edit'),
    path('employees/<int:pk>/delete/', views.employee_delete_view, name='employee_delete'),
]