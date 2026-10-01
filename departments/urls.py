from django.urls import path
from . import views

urlpatterns = [
    path('', views.department_list_view, name='department_list'),
    path('add/', views.department_create_view, name='department_add'),
    path('<int:pk>/edit/', views.department_update_view, name='department_edit'),
    path('<int:pk>/delete/', views.department_delete_view, name='department_delete'),
    path('designations/add/', views.designation_create_view, name='designation_add'),
]