from django.db import models
from employees.models import Employee


class SalaryRecord(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('CANCELLED', 'Cancelled'),
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='salary_records'
    )
    month = models.PositiveSmallIntegerField(help_text="Month number 1 to 12")
    year = models.PositiveIntegerField()
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    payment_date = models.DateField(blank=True, null=True)
    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOICES,
        default='PENDING'
    )
    remarks = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-year', '-month']
        constraints = [
            models.UniqueConstraint(
                fields=['employee', 'month', 'year'],
                name='unique_salary_per_month'
            )
        ]

    def save(self, *args, **kwargs):
        # Auto-calculate net salary: Basic + Allowance + Bonus - Deduction
        self.net_salary = (
            (self.basic_salary or 0)
            + (self.allowance or 0)
            + (self.bonus or 0)
            - (self.deduction or 0)
        )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.employee_id} - {self.month}/{self.year} (₹{self.net_salary})"