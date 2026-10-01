from django import forms
from .models import Department, Designation


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Information Technology, Finance'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief summary of department responsibilities...'
            }),
        }


class DesignationForm(forms.ModelForm):
    class Meta:
        model = Designation
        fields = ['department', 'title', 'description']
        widgets = {
            'department': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Software Engineer, HR Specialist'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Role scope and responsibilities...'
            }),
        }