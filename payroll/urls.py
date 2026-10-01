from django.urls import path
from . import views

urlpatterns = [
    # HR / Admin management
    path('', views.salary_list_view, name='salary_list'),
    path('add/', views.salary_create_view, name='salary_add'),
    path('<int:pk>/', views.salary_detail_view, name='salary_detail'),
    path('<int:pk>/edit/', views.salary_update_view, name='salary_edit'),

    # Employee self-service
    path('my/', views.my_salary_view, name='my_salary'),
]