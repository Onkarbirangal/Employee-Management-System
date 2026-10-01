from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_redirect_view, name='home'),
    path('login/', views.user_login_view, name='login'),
    path('register/', views.user_register_view, name='register'),
    path('logout/', views.user_logout_view, name='logout'),
    path('dashboard-redirect/', views.login_redirect_view, name='login_redirect'),
    path('change-password/', views.change_password_view, name='change_password'),
]