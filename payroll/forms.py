from django import forms
from django.utils import timezone
from .models import SalaryRecord
from employees.models import Employee


class SalaryRecordForm(forms.ModelForm):
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.filter(status='ACTIVE').select_related('user'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = SalaryRecord
        fields = [
            'employee',
            'month',
            'year',
            'basic_salary',
            'allowance',
            'bonus',
            'deduction',
            'payment_date',
            'payment_status',
            'remarks',
        ]
        widgets = {
            'month': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 12}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'min': 2020, 'max': 2035}),
            'basic_salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'allowance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'bonus': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'deduction': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'payment_status': forms.Select(attrs={'class': 'form-select'}),
            'remarks': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional payment reference or note'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        employee = cleaned_data.get('employee')
        month = cleaned_data.get('month')
        year = cleaned_data.get('year')

        if employee and month and year:
            query = SalaryRecord.objects.filter(employee=employee, month=month, year=year)
            if self.instance.pk:
                query = query.exclude(pk=self.instance.pk)
            if query.exists():
                raise forms.ValidationError(
                    f"A salary record for {employee.full_name} for {month}/{year} has already been created."
                )

        return cleaned_data