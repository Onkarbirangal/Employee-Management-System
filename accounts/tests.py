from django.test import TestCase, Client
from django.contrib.auth.models import User
from employees.models import Employee
from departments.models import Department


class RoleAccessSecurityTests(TestCase):
    def setUp(self):
        self.client = Client()

        # 1. Create Master Admin
        self.admin_user = User.objects.create_superuser(
            username='admin_test',
            email='admin@test.com',
            password='AdminPassword123'
        )

        # 2. Create HR User
        self.hr_user = User.objects.create_user(
            username='hr_test',
            email='hr@test.com',
            password='HrPassword123'
        )
        self.hr_employee = Employee.objects.create(
            user=self.hr_user,
            employee_id='HR-001',
            role='HR',
            status='ACTIVE'
        )

        # 3. Create Standard Employee
        self.emp_user = User.objects.create_user(
            username='emp_test',
            email='emp@test.com',
            password='EmpPassword123'
        )
        self.emp_employee = Employee.objects.create(
            user=self.emp_user,
            employee_id='EMP-001',
            role='EMPLOYEE',
            status='ACTIVE'
        )

    def test_anonymous_user_redirects_to_login(self):
        """Unauthenticated requests must redirect directly to login."""
        response = self.client.get('/admin-dashboard/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_employee_cannot_access_admin_dashboard(self):
        """A normal employee accessing admin dashboard must receive 403 Forbidden."""
        self.client.login(username='emp_test', password='EmpPassword123')
        response = self.client.get('/admin-dashboard/')
        self.assertEqual(response.status_code, 403)

    def test_employee_cannot_access_hr_dashboard(self):
        """A normal employee accessing HR dashboard must receive 403 Forbidden."""
        self.client.login(username='emp_test', password='EmpPassword123')
        response = self.client.get('/hr-dashboard/')
        self.assertEqual(response.status_code, 403)

    def test_hr_cannot_access_admin_dashboard(self):
        """HR managers must be blocked from executive admin dashboard."""
        self.client.login(username='hr_test', password='HrPassword123')
        response = self.client.get('/admin-dashboard/')
        self.assertEqual(response.status_code, 403)

    def test_admin_can_access_admin_dashboard(self):
        """Admins must successfully load the admin dashboard."""
        self.client.login(username='admin_test', password='AdminPassword123')
        response = self.client.get('/admin-dashboard/')
        self.assertEqual(response.status_code, 200)