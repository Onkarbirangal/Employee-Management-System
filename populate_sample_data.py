import os
import django
from datetime import date, time, timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'employee_management.settings')
django.setup()

from django.contrib.auth.models import User
from departments.models import Department, Designation
from employees.models import Employee
from attendance.models import Attendance
from leaves.models import LeaveRequest
from payroll.models import SalaryRecord
from notifications.models import Notification


def run_seed():
    print("🚀 Seeding Employee Management System Database...")

    # 1. Create Departments
    it_dept, _ = Department.objects.get_or_create(
        name="Information Technology",
        defaults={"description": "Software architecture, web development, and cloud services."}
    )
    hr_dept, _ = Department.objects.get_or_create(
        name="Human Resources",
        defaults={"description": "Talent acquisition, payroll, and corporate culture."}
    )
    finance_dept, _ = Department.objects.get_or_create(
        name="Finance & Accounts",
        defaults={"description": "Audits, financial budgeting, and accounting."}
    )

    # 2. Create Designations
    dev_des, _ = Designation.objects.get_or_create(
        department=it_dept,
        title="Software Developer",
        defaults={"description": "Django and Full-Stack Engineering"}
    )
    lead_des, _ = Designation.objects.get_or_create(
        department=it_dept,
        title="Technical Lead",
        defaults={"description": "System architecture and team lead"}
    )
    hr_exec_des, _ = Designation.objects.get_or_create(
        department=hr_dept,
        title="HR Executive",
        defaults={"description": "Employee onboarding and leave processing"}
    )

    # 3. Create Sample Users & Profiles
    # --- Role A: HR User ---
    hr_user, _ = User.objects.get_or_create(
        username="hr_manager",
        defaults={
            "email": "hr@company.com",
            "first_name": "Pooja",
            "last_name": "Sharma"
        }
    )
    hr_user.set_password("HrPass@123")
    hr_user.save()

    hr_profile, _ = Employee.objects.get_or_create(
        user=hr_user,
        defaults={
            "employee_id": "HR-101",
            "phone": "+91 9823011223",
            "gender": "FEMALE",
            "department": hr_dept,
            "designation": hr_exec_des,
            "joining_date": date(2025, 1, 15),
            "basic_salary": 65000.00,
            "role": "HR",
            "status": "ACTIVE"
        }
    )

    # --- Role B: Regular Employee 1 ---
    emp1_user, _ = User.objects.get_or_create(
        username="rahul_dev",
        defaults={
            "email": "rahul@company.com",
            "first_name": "Rahul",
            "last_name": "Verma"
        }
    )
    emp1_user.set_password("EmpPass@123")
    emp1_user.save()

    emp1_profile, _ = Employee.objects.get_or_create(
        user=emp1_user,
        defaults={
            "employee_id": "EMP-201",
            "phone": "+91 9876543210",
            "gender": "MALE",
            "department": it_dept,
            "designation": dev_des,
            "joining_date": date(2025, 3, 1),
            "basic_salary": 55000.00,
            "role": "EMPLOYEE",
            "status": "ACTIVE"
        }
    )

    # --- Role C: Regular Employee 2 ---
    emp2_user, _ = User.objects.get_or_create(
        username="priya_tech",
        defaults={
            "email": "priya@company.com",
            "first_name": "Priya",
            "last_name": "Patil"
        }
    )
    emp2_user.set_password("EmpPass@123")
    emp2_user.save()

    emp2_profile, _ = Employee.objects.get_or_create(
        user=emp2_user,
        defaults={
            "employee_id": "EMP-202",
            "phone": "+91 9988776655",
            "gender": "FEMALE",
            "department": it_dept,
            "designation": lead_des,
            "joining_date": date(2024, 8, 10),
            "basic_salary": 85000.00,
            "role": "EMPLOYEE",
            "status": "ACTIVE"
        }
    )

    # 4. Create Attendance Logs (Today & Yesterday)
    today = date.today()
    yesterday = today - timedelta(days=1)

    Attendance.objects.get_or_create(
        employee=emp1_profile,
        date=today,
        defaults={"check_in": time(9, 15), "status": "PRESENT"}
    )
    Attendance.objects.get_or_create(
        employee=emp2_profile,
        date=today,
        defaults={"check_in": time(9, 30), "status": "PRESENT"}
    )
    Attendance.objects.get_or_create(
        employee=emp1_profile,
        date=yesterday,
        defaults={"check_in": time(9, 10), "check_out": time(18, 5), "status": "PRESENT"}
    )

    # 5. Create Sample Leave Requests
    LeaveRequest.objects.get_or_create(
        employee=emp1_profile,
        start_date=today + timedelta(days=5),
        end_date=today + timedelta(days=7),
        defaults={
            "leave_type": "CASUAL",
            "reason": "Attending family function in native town.",
            "status": "PENDING"
        }
    )
    LeaveRequest.objects.get_or_create(
        employee=emp2_profile,
        start_date=today - timedelta(days=10),
        end_date=today - timedelta(days=8),
        defaults={
            "leave_type": "SICK",
            "reason": "Viral fever recovery.",
            "status": "APPROVED",
            "approved_by": hr_user
        }
    )

    # 6. Create Salary Records
    SalaryRecord.objects.get_or_create(
        employee=emp1_profile,
        month=8,
        year=2026,
        defaults={
            "basic_salary": 55000.00,
            "allowance": 5000.00,
            "bonus": 2500.00,
            "deduction": 3200.00,
            "payment_date": date(2026, 8, 31),
            "payment_status": "PAID"
        }
    )
    SalaryRecord.objects.get_or_create(
        employee=emp2_profile,
        month=8,
        year=2026,
        defaults={
            "basic_salary": 85000.00,
            "allowance": 8000.00,
            "bonus": 5000.00,
            "deduction": 6200.00,
            "payment_date": date(2026, 8, 31),
            "payment_status": "PAID"
        }
    )

    # 7. Create Notifications
    Notification.objects.get_or_create(
        recipient=emp1_user,
        title="August Salary Disbursed",
        defaults={
            "message": "Your payslip for August 2026 has been generated.",
            "notification_type": "PAYROLL",
            "is_read": False,
            "link": "/payroll/my/"
        }
    )

    print("✅ Sample seed data created successfully!")


if __name__ == '__main__':
    run_seed()