from django.urls import path
from . import views

urlpatterns = [
    # HR / Admin management
    path('', views.attendance_list_view, name='attendance_list'),
    path('add/', views.attendance_create_view, name='attendance_add'),
    path('<int:pk>/edit/', views.attendance_update_view, name='attendance_edit'),

    # Employee self-service
    path('my/', views.my_attendance_view, name='my_attendance'),
    path('clock-in/', views.clock_in_view, name='clock_in_view'),
    path('clock-out/', views.clock_out_view, name='clock_out_view'),
]