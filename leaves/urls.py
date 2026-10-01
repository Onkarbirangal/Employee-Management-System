from django.urls import path
from . import views

urlpatterns = [
    path('', views.leave_list_view, name='leave_list'),
    path('apply/', views.leave_apply_view, name='leave_apply'),
    path('my/', views.my_leaves_view, name='my_leaves'),
    path('<int:pk>/action/', views.leave_action_view, name='leave_action'),
]