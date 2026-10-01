from django.test import TestCase, Client
from django.contrib.auth.models import User
from employees.models import Employee
from payroll.models import SalaryRecord


class EmployeePrivacyAndPayrollTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Employee 1
        self.user1 = User.objects.create_user(username='user1', password='Password123')
        self.emp1 = Employee.objects.create(user=self.user1, employee_id='EMP-01', role='EMPLOYEE', status='ACTIVE')

        # Employee 2
        self.user2 = User.objects.create_user(username='user2', password='Password123')
        self.emp2 = Employee.objects.create(user=self.user2, employee_id='EMP-02', role='EMPLOYEE', status='ACTIVE')

        # Payslip for Employee 2
        self.salary2 = SalaryRecord.objects.create(
            employee=self.emp2,
            month=5,
            year=2026,
            basic_salary=50000.00,
            allowance=5000.00,
            bonus=2000.00,
            deduction=3000.00,
            payment_status='PAID'
        )

    def test_net_salary_calculation(self):
        """Verify formula: Net = Basic + Allowance + Bonus - Deduction."""
        # 50000 + 5000 + 2000 - 3000 = 54000
        self.assertEqual(self.salary2.net_salary, 54000.00)

    def test_employee_cannot_view_others_profile(self):
        """User 1 must be blocked or redirected when attempting to view User 2's profile."""
        self.client.login(username='user1', password='Password123')
        response = self.client.get(f'/employees/{self.emp2.pk}/')
        # Expect redirect back to dashboard due to ownership check
        self.assertEqual(response.status_code, 302)
        self.assertIn('/employee-dashboard/', response.url)

    def test_employee_cannot_view_others_salary_slip(self):
        """User 1 must not be able to inspect User 2's salary slip."""
        self.client.login(username='user1', password='Password123')
        response = self.client.get(f'/payroll/{self.salary2.pk}/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/payroll/my/', response.url)