from django.contrib import admin
from .models import Department, Designation


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'department', 'created_at')
    list_filter = ('department',)
    search_fields = ('title', 'department__name')
    ordering = ('department', 'title')