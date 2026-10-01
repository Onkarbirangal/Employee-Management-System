from django.urls import path
from . import views

urlpatterns = [
    path('', views.reports_hub_view, name='reports_hub'),
]