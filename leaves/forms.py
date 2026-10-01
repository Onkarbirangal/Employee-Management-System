from django import forms
from django.utils import timezone
from .models import LeaveRequest


class LeaveApplyForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'leave_type': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Explain the context or reason for this leave application...'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        today = timezone.now().date()

        if start_date:
            if start_date < today:
                self.add_error('start_date', "Start date cannot be in the past.")

        if start_date and end_date:
            if end_date < start_date:
                self.add_error('end_date', "End date cannot be prior to start date.")

        return cleaned_data


class LeaveActionForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['status', 'rejection_reason']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'rejection_reason': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Provide justification if rejecting this request...'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        rejection_reason = cleaned_data.get('rejection_reason')

        if status == 'REJECTED' and not rejection_reason:
            self.add_error('rejection_reason', "Please enter a reason when rejecting a leave request.")

        return cleaned_data