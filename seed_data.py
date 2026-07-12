"""
GLIDE Institute - Complete Database Seed Script (UNIFIED)
This script wipes all data and creates fresh seed data with everything.
Run with: python manage.py shell < seed_full.py
Or during deployment: python manage.py shell -c "exec(open('seed_full.py').read())"
"""

import os
import sys
import django
from datetime import date, timedelta, datetime
from decimal import Decimal
import random
from django.db import transaction, models
from django.contrib.auth.hashers import make_password

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glide_sms.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction
from core.models import (
    User, Department, Course, CourseCategory, Class, Student, StudentApplication
)
from admissions.models import AcademicYear, Semester, AdmissionBatch, AdmittedStudent
from academics.models import CourseUnit, Assessment, Result, StudentCourseProgress, AttendanceRecord, Timetable
from finance.models import FeeStructure, Invoice, Payment, FinancialClearance
from hr.models import Employee, LeaveRequest, Attendance as HRAttendance

User = get_user_model()

# ============================================
# CONFIGURATION
# ============================================
STUDENT_COUNT = 50
ACADEMIC_YEAR = "2024/2025"
SEMESTER = "semester1"

# ============================================
# HELPER FUNCTIONS
# ============================================
def random_date(start_date, end_date):
    """Generate a random date between start and end"""
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)

def random_phone():
    """Generate a random Ugandan phone number"""
    return f"077{random.randint(100000, 999999)}"

def random_grade():
    """Generate a random grade with weighted distribution"""
    weights = ['A'] * 15 + ['B+'] * 20 + ['B'] * 25 + ['C+'] * 20 + ['C'] * 15 + ['D'] * 4 + ['F'] * 1
    return random.choice(weights)

def grade_to_score(grade):
    """Convert grade to a score"""
    mapping = {
        'A': random.randint(80, 100),
        'B+': random.randint(75, 79),
        'B': random.randint(70, 74),
        'C+': random.randint(65, 69),
        'C': random.randint(55, 64),
        'D': random.randint(40, 54),
        'F': random.randint(0, 39)
    }
    return mapping.get(grade, random.randint(50, 70))

def create_password():
    """Generate a random password"""
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*'
    return ''.join(random.choice(chars) for _ in range(12))

# ============================================
# 1. WIPE ALL DATA
# ============================================
print("="*70)
print("GLIDE INSTITUTE - COMPLETE DATABASE WIPE & RESEED")
print("="*70)

print("\n🗑️ Wiping existing data...")

with transaction.atomic():
    # Delete in correct order to avoid foreign key constraints
    AttendanceRecord.objects.all().delete()
    Result.objects.all().delete()
    StudentCourseProgress.objects.all().delete()
    Assessment.objects.all().delete()
    Timetable.objects.all().delete()
    Invoice.objects.all().delete()
    Payment.objects.all().delete()
    FinancialClearance.objects.all().delete()
    FeeStructure.objects.all().delete()
    AdmittedStudent.objects.all().delete()
    StudentApplication.objects.all().delete()
    Student.objects.all().delete()
    Class.objects.all().delete()
    CourseUnit.objects.all().delete()
    Course.objects.all().delete()
    CourseCategory.objects.all().delete()
    Department.objects.all().delete()
    Semester.objects.all().delete()
    AcademicYear.objects.all().delete()
    AdmissionBatch.objects.all().delete()
    LeaveRequest.objects.all().delete()
    HRAttendance.objects.all().delete()
    Employee.objects.all().delete()
    User.objects.filter(is_superuser=False).delete()

print("✅ All data wiped successfully!")

# ============================================
# 2. CREATE USERS
# ============================================
print("\n👤 Creating users...")

users_data = [
    # Super Admin
    {'username': 'superadmin', 'email': 'superadmin@glideafrica.org', 'password': 'Super@2024', 'first_name': 'Super', 'last_name': 'Admin', 'user_type': 'super_admin', 'is_superuser': True, 'is_staff': True},
    
    # Admin
    {'username': 'admin', 'email': 'admin@glideafrica.org', 'password': 'Admin@2024', 'first_name': 'System', 'last_name': 'Admin', 'user_type': 'admin', 'is_superuser': False, 'is_staff': True},
    {'username': 'registrar', 'email': 'registrar@glideafrica.org', 'password': 'Registrar@2024', 'first_name': 'Registration', 'last_name': 'Officer', 'user_type': 'registrar', 'is_superuser': False, 'is_staff': True},
    
    # Staff & Lecturers
    {'username': 'staff', 'email': 'staff@glideafrica.org', 'password': 'Staff@2024', 'first_name': 'Staff', 'last_name': 'Member', 'user_type': 'staff', 'is_superuser': False, 'is_staff': True},
    {'username': 'lecturer', 'email': 'lecturer@glideafrica.org', 'password': 'Lecturer@2024', 'first_name': 'Senior', 'last_name': 'Lecturer', 'user_type': 'lecturer', 'is_superuser': False, 'is_staff': True},
    
    # Finance
    {'username': 'finance', 'email': 'finance@glideafrica.org', 'password': 'Finance@2024', 'first_name': 'Finance', 'last_name': 'Officer', 'user_type': 'finance', 'is_superuser': False, 'is_staff': True},
    
    # HR
    {'username': 'hr', 'email': 'hr@glideafrica.org', 'password': 'HR@2024', 'first_name': 'HR', 'last_name': 'Manager', 'user_type': 'hr', 'is_superuser': False, 'is_staff': True},
]

users_created = {}
for user_data in users_data:
    try:
        if user_data['is_superuser']:
            user = User.objects.create_superuser(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name']
            )
        else:
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name']
            )
        user.user_type = user_data['user_type']
        user.is_staff = user_data['is_staff']
        user.save()
        users_created[user.username] = user
        print(f"  ✅ {user_data['username']} ({user_data['user_type']})")
    except Exception as e:
        print(f"  ❌ Failed to create {user_data['username']}: {e}")

# ============================================
# 3. CREATE DEPARTMENTS
# ============================================
print("\n🏢 Creating departments...")

departments_data = [
    {'name': 'Engineering', 'code': 'ENG', 'description': 'Engineering Department'},
    {'name': 'Business Studies', 'code': 'BUS', 'description': 'Business and Commerce Department'},
    {'name': 'Information Technology', 'code': 'ICT', 'description': 'IT and Computer Science Department'},
    {'name': 'Agriculture', 'code': 'AGR', 'description': 'Agriculture Department'},
    {'name': 'Hospitality', 'code': 'HOS', 'description': 'Hospitality and Tourism Department'},
]

departments = {}
for dept_data in departments_data:
    dept = Department.objects.create(
        name=dept_data['name'],
        code=dept_data['code'],
        description=dept_data['description']
    )
    departments[dept.code] = dept
    print(f"  ✅ {dept.name} ({dept.code})")

# ============================================
# 4. CREATE COURSE CATEGORIES
# ============================================
print("\n📚 Creating course categories...")

categories_data = [
    {'name': 'Diploma', 'category_type': 'diploma'},
    {'name': 'Certificate', 'category_type': 'certificate'},
    {'name': 'Occupational', 'category_type': 'occupational'},
    {'name': 'Modular', 'category_type': 'modular'},
]

categories = {}
for cat_data in categories_data:
    cat = CourseCategory.objects.create(
        name=cat_data['name'],
        category_type=cat_data['category_type']
    )
    categories[cat.category_type] = cat
    print(f"  ✅ {cat.name} ({cat.category_type})")

# ============================================
# 5. CREATE COURSES
# ============================================
print("\n📚 Creating courses...")

courses_data = [
    # Diploma Programs
    {'name': 'Diploma in Information Technology', 'code': 'DIT', 'category_type': 'diploma', 'department_code': 'ICT', 'duration': '2_years', 'tuition_fee': 2500000, 'application_fee': 50000},
    {'name': 'Diploma in Business Administration', 'code': 'DBA', 'category_type': 'diploma', 'department_code': 'BUS', 'duration': '2_years', 'tuition_fee': 2200000, 'application_fee': 50000},
    {'name': 'Diploma in Mechanical Engineering', 'code': 'DME', 'category_type': 'diploma', 'department_code': 'ENG', 'duration': '2_years', 'tuition_fee': 2800000, 'application_fee': 50000},
    {'name': 'Diploma in Electrical Engineering', 'code': 'DEE', 'category_type': 'diploma', 'department_code': 'ENG', 'duration': '2_years', 'tuition_fee': 2700000, 'application_fee': 50000},
    
    # Certificate Programs
    {'name': 'Certificate in Information Technology', 'code': 'CIT', 'category_type': 'certificate', 'department_code': 'ICT', 'duration': '2_years', 'tuition_fee': 1500000, 'application_fee': 50000},
    {'name': 'Certificate in Business Administration', 'code': 'CBA', 'category_type': 'certificate', 'department_code': 'BUS', 'duration': '2_years', 'tuition_fee': 1300000, 'application_fee': 50000},
    
    # Occupational Programs
    {'name': 'Motor Vehicle Repair and Maintenance', 'code': 'MVR', 'category_type': 'occupational', 'department_code': 'ENG', 'duration': '2_years', 'tuition_fee': 1200000, 'application_fee': 30000},
    {'name': 'Tailoring and Garment Design', 'code': 'TGD', 'category_type': 'occupational', 'department_code': 'BUS', 'duration': '2_years', 'tuition_fee': 1000000, 'application_fee': 30000},
]

courses = {}
for course_data in courses_data:
    category = categories.get(course_data['category_type'])
    dept = departments.get(course_data['department_code'])
    course = Course.objects.create(
        name=course_data['name'],
        code=course_data['code'],
        category=category,
        department=dept,
        duration=course_data['duration'],
        entry_requirements=f"Entry requirements for {course_data['name']}",
        description=f"Description for {course_data['name']}",
        tuition_fee=course_data['tuition_fee'],
        application_fee=course_data['application_fee'],
        is_active=True
    )
    courses[course.code] = course
    print(f"  ✅ {course.name} ({course.code})")

# ============================================
# 6. CREATE CLASSES
# ============================================
print("\n🏫 Creating classes...")

classes = {}
for course_code, course in courses.items():
    class_obj = Class.objects.create(
        name=f"{course.name} - Year 1",
        code=f"CLS-{course_code}-2024",
        course=course,
        academic_year=ACADEMIC_YEAR,
        semester=SEMESTER,
        start_date=date(2024, 8, 1),
        end_date=date(2024, 12, 15),
        capacity=50,
        current_enrollment=0,
        is_active=True
    )
    classes[course_code] = class_obj
    print(f"  ✅ {class_obj.name}")

# ============================================
# 7. CREATE ACADEMIC YEAR & SEMESTER
# ============================================
print("\n📅 Creating academic years and semesters...")

academic_year = AcademicYear.objects.create(
    name=ACADEMIC_YEAR,
    start_date=date(2024, 8, 1),
    end_date=date(2025, 7, 31),
    is_current=True
)
print(f"  ✅ {academic_year.name}")

semester1 = Semester.objects.create(
    academic_year=academic_year,
    name='semester1',
    start_date=date(2024, 8, 1),
    end_date=date(2024, 12, 15),
    is_current=True,
    registration_deadline=date(2024, 8, 15)
)
print(f"  ✅ {semester1.get_name_display()}")

semester2 = Semester.objects.create(
    academic_year=academic_year,
    name='semester2',
    start_date=date(2025, 1, 15),
    end_date=date(2025, 5, 30),
    is_current=False,
    registration_deadline=date(2025, 1, 30)
)
print(f"  ✅ {semester2.get_name_display()}")

# ============================================
# 8. CREATE COURSE UNITS
# ============================================
print("\n📚 Creating course units...")

unit_data = {
    'DIT': [
        ('Introduction to Programming', 'DIT101', 3),
        ('Database Management', 'DIT102', 3),
        ('Network Fundamentals', 'DIT103', 3),
        ('Web Development', 'DIT104', 3),
        ('Systems Analysis', 'DIT105', 3),
        ('Operating Systems', 'DIT106', 3),
    ],
    'DBA': [
        ('Principles of Management', 'DBA101', 3),
        ('Financial Accounting', 'DBA102', 3),
        ('Marketing Management', 'DBA103', 3),
        ('Entrepreneurship', 'DBA104', 3),
        ('Business Law', 'DBA105', 3),
        ('Human Resource Management', 'DBA106', 3),
    ],
    'DME': [
        ('Engineering Mathematics', 'DME101', 3),
        ('Thermodynamics', 'DME102', 3),
        ('Materials Science', 'DME103', 3),
        ('Machine Design', 'DME104', 3),
        ('Manufacturing Processes', 'DME105', 3),
    ],
    'CIT': [
        ('Introduction to Computing', 'CIT101', 3),
        ('Microsoft Office Applications', 'CIT102', 3),
        ('Internet and Email', 'CIT103', 3),
        ('Computer Hardware', 'CIT104', 3),
    ],
}

for course_code, units in unit_data.items():
    course = courses.get(course_code)
    if course:
        for name, code, credits in units:
            unit = CourseUnit.objects.create(
                name=name,
                code=code,
                course=course,
                credit_hours=credits,
                is_core=True
            )
            print(f"  ✅ {code} - {name}")

# ============================================
# 9. CREATE FEE STRUCTURES
# ============================================
print("\n💰 Creating fee structures...")

fee_types = ['tuition', 'application', 'exam', 'library', 'activity']
for course in courses.values():
    for fee_type in fee_types:
        amount = course.tuition_fee if fee_type == 'tuition' else random.randint(30000, 150000)
        FeeStructure.objects.create(
            course=course,
            fee_type=fee_type,
            amount=amount,
            academic_year=ACADEMIC_YEAR,
            is_required=True,
            is_active=True
        )
    print(f"  ✅ Fee structures for {course.name}")

# ============================================
# 10. CREATE STUDENTS
# ============================================
print(f"\n👨‍🎓 Creating {STUDENT_COUNT} students...")

first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Mary', 'James', 'Patricia', 'Robert', 'Jennifer',
               'William', 'Linda', 'Richard', 'Elizabeth', 'Joseph', 'Susan', 'Thomas', 'Jessica', 'Charles', 'Margaret',
               'Christopher', 'Lisa', 'Daniel', 'Nancy', 'Matthew', 'Helen', 'Anthony', 'Sandra', 'Donald', 'Donna',
               'Mark', 'Carol', 'Paul', 'Ruth', 'Steven', 'Sharon', 'Andrew', 'Michelle', 'Joshua', 'Laura',
               'Kenneth', 'Kimberly', 'Kevin', 'Deborah', 'Brian', 'Amy', 'George', 'Angela', 'Timothy', 'Pamela']

last_names = ['Mukasa', 'Nabatanzi', 'Ssali', 'Nakintu', 'Lubega', 'Nalubega', 'Kato', 'Nansubuga', 'Ssenyonga', 'Nakato',
              'Lule', 'Nabukenya', 'Muwonge', 'Namatovu', 'Kalema', 'Nakayiwa', 'Ssekandi', 'Nambi', 'Mugisha', 'Nakayenze',
              'Tumusiime', 'Nantongo', 'Kisakye', 'Nakamanya', 'Sserwadda', 'Nakayiza', 'Luwaga', 'Nabirye', 'Mugerwa', 'Nakibuuka']

gender_options = ['male', 'female']
status_options = ['active', 'active', 'active', 'active', 'active', 'graduated', 'inactive', 'suspended']
course_list = list(courses.items())

students_created = []
for i in range(STUDENT_COUNT):
    try:
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        username = f"{first_name.lower()}.{last_name.lower()}{random.randint(10, 99)}"
        email = f"{username}@glide.edu"
        gender = random.choice(gender_options)
        dob = random_date(date(1995, 1, 1), date(2005, 12, 31))
        course_code, course = random.choice(course_list)
        class_obj = classes.get(course_code)
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password='Student@2024',
            first_name=first_name,
            last_name=last_name,
            user_type='student',
            phone=random_phone()
        )
        
        # Create student
        student = Student.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=dob,
            gender=gender,
            nationality='Ugandan',
            marital_status=random.choice(['single', 'single', 'single', 'married']),
            course=course,
            current_class=class_obj,
            status=random.choice(status_options),
            phone=random_phone(),
            email=email,
            address=f"{random.randint(1, 100)} Kampala Road",
            district=random.choice(['Kampala', 'Wakiso', 'Mukono', 'Jinja', 'Butaleja', 'Tororo', 'Mbale']),
            village=random.choice(['Kampala', 'Ntinda', 'Bukoto', 'Naguru', 'Muyenga', 'Kiwatule']),
            parent_name=f"{random.choice(['Mr.', 'Mrs.'])} {random.choice(last_names)}",
            parent_phone=random_phone()
        )
        
        # Update class enrollment
        if class_obj:
            class_obj.current_enrollment += 1
            class_obj.save()
        
        students_created.append(student)
        print(f"  ✅ {i+1}. {student.registration_number} - {student.full_name} ({course.name})")
        
        # ============================================
        # 11. CREATE APPLICATION
        # ============================================
        app = StudentApplication.objects.create(
            application_id=f"APP/2024/{i+1:04d}",
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=random_phone(),
            course_type=course.category.category_type if course.category else 'diploma',
            program_applied=course.name,
            status='admitted',
            application_date=random_date(date(2024, 6, 1), date(2024, 7, 31)),
            declaration_agreed=True,
            declaration_signature=f"{first_name} {last_name}",
            declaration_date=random_date(date(2024, 6, 1), date(2024, 7, 31))
        )
        
        # ============================================
        # 12. CREATE ADMISSION
        # ============================================
        AdmittedStudent.objects.create(
            application=app,
            student=student,
            admission_date=random_date(date(2024, 7, 1), date(2024, 8, 31)),
            confirmed_enrollment=True,
            confirmed_enrollment_date=random_date(date(2024, 8, 1), date(2024, 8, 15))
        )
        
        # ============================================
        # 13. CREATE ACADEMIC PROGRESS & RESULTS
        # ============================================
        course_units = CourseUnit.objects.filter(course=course)
        for unit in course_units:
            grade = random_grade()
            score = grade_to_score(grade)
            is_passed = grade != 'F'
            
            StudentCourseProgress.objects.create(
                student=student,
                course_unit=unit,
                semester=semester1,
                score=score,
                grade=grade,
                is_completed=True,
                is_retake=False,
                is_passed=is_passed
            )
            
            assessment = Assessment.objects.create(
                name=f"{unit.name} - Final Exam",
                course_unit=unit,
                class_obj=class_obj,
                assessment_type='final',
                max_score=100,
                weight=50,
                date=random_date(date(2024, 11, 1), date(2024, 12, 10)),
                duration_minutes=120,
                semester=semester1,
                is_published=True,
                is_closed=True
            )
            
            Result.objects.create(
                student=student,
                course_unit=unit,
                assessment=assessment,
                score=score,
                grade=grade,
                semester=semester1,
                is_published=True,
                published_date=random_date(date(2024, 12, 1), date(2024, 12, 15))
            )
        
        # ============================================
        # 14. CREATE ATTENDANCE
        # ============================================
        start_date = date(2024, 8, 15)
        end_date = date(2024, 11, 30)
        current_date = start_date
        attendance_statuses = ['present'] * 70 + ['absent'] * 10 + ['late'] * 15 + ['excused'] * 5
        
        while current_date <= end_date:
            if current_date.weekday() < 5:
                for unit in course_units[:3]:
                    AttendanceRecord.objects.create(
                        student=student,
                        class_obj=class_obj,
                        course_unit=unit,
                        date=current_date,
                        status=random.choice(attendance_statuses),
                        time_in=random.choice([None, '08:00', '08:15', '08:30', '09:00']),
                        time_out=random.choice([None, '16:00', '16:30', '17:00'])
                    )
            current_date += timedelta(days=1)
        
        # ============================================
        # 15. CREATE FINANCIAL RECORDS
        # ============================================
        fee_structures = FeeStructure.objects.filter(course=course, academic_year=ACADEMIC_YEAR)
        total_fee = sum(f.amount for f in fee_structures)
        
        invoice = Invoice.objects.create(
            student=student,
            semester=semester1,
            invoice_number=f"INV/{ACADEMIC_YEAR[:4]}/{student.id:04d}",
            issue_date=random_date(date(2024, 8, 1), date(2024, 8, 10)),
            due_date=random_date(date(2024, 9, 1), date(2024, 9, 30)),
            total_amount=total_fee,
            status='fully_paid' if random.random() > 0.2 else 'partially_paid'
        )
        
        if random.random() < 0.7:
            payment_amount = total_fee
            payment_date = random_date(date(2024, 8, 15), date(2024, 9, 15))
            Payment.objects.create(
                invoice=invoice,
                student=student,
                amount=payment_amount,
                payment_date=payment_date,
                payment_method=random.choice(['cash', 'bank', 'mobile']),
                receipt_number=f"REC/{payment_date.year}/{random.randint(1000, 9999)}",
                recorded_by=None
            )
            invoice.amount_paid = payment_amount
            invoice.balance = 0
            invoice.status = 'fully_paid'
            invoice.save()
            
        elif random.random() < 0.9:
            payment_amount = total_fee * Decimal(random.uniform(0.3, 0.7))
            payment_date = random_date(date(2024, 8, 15), date(2024, 9, 30))
            Payment.objects.create(
                invoice=invoice,
                student=student,
                amount=payment_amount,
                payment_date=payment_date,
                payment_method=random.choice(['cash', 'bank', 'mobile']),
                receipt_number=f"REC/{payment_date.year}/{random.randint(1000, 9999)}",
                recorded_by=None
            )
            invoice.amount_paid = payment_amount
            invoice.balance = total_fee - payment_amount
            invoice.status = 'partially_paid'
            invoice.save()
        
        FinancialClearance.objects.create(
            student=student,
            semester=semester1,
            is_cleared=True if random.random() < 0.8 else False,
            clearance_date=random_date(date(2024, 9, 1), date(2024, 10, 15)) if random.random() < 0.8 else None,
            notes="Cleared - All fees paid" if random.random() < 0.8 else "Pending payment"
        )
        
    except Exception as e:
        print(f"  ❌ Failed to create student: {e}")

# ============================================
# 16. CREATE EMPLOYEES
# ============================================
print("\n👤 Creating employees...")

employee_roles = ['admin', 'staff', 'lecturer', 'registrar', 'finance', 'hr']
for user in User.objects.filter(user_type__in=employee_roles):
    Employee.objects.create(
        user=user,
        employee_number=f"EMP/{ACADEMIC_YEAR[:4]}/{user.id:04d}",
        position=f"{user.user_type.title()} Officer",
        employment_type='full_time',
        employment_date=date(2024, 1, 1),
        status='active',
        salary=random.randint(1000000, 5000000)
    )
    print(f"  ✅ Employee created for {user.username}")

# ============================================
# 17. CREATE TIMETABLE
# ============================================
print("\n⏰ Creating timetables...")

days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
times = [('08:00', '09:00'), ('09:00', '10:00'), ('10:00', '11:00'), ('11:00', '12:00'), ('14:00', '15:00'), ('15:00', '16:00')]

for class_obj in classes.values():
    units = CourseUnit.objects.filter(course=class_obj.course)[:4]
    for i, unit in enumerate(units):
        if i < len(times):
            day = days[i % len(days)]
            start_time, end_time = times[i]
            Timetable.objects.create(
                class_obj=class_obj,
                course_unit=unit,
                lecturer=User.objects.filter(user_type='lecturer').first(),
                day_of_week=day,
                start_time=start_time,
                end_time=end_time,
                venue=f"Room {random.randint(101, 500)}",
                semester=semester1,
                is_active=True
            )
            print(f"  ✅ Timetable entry for {unit.name}")

# ============================================
# 18. FINAL SUMMARY
# ============================================
print("\n" + "="*70)
print("✅ SEED DATA COMPLETE!")
print("="*70)

print("\n📊 Summary:")
print(f"  • Users: {User.objects.count()}")
print(f"  • Departments: {Department.objects.count()}")
print(f"  • Course Categories: {CourseCategory.objects.count()}")
print(f"  • Courses: {Course.objects.count()}")
print(f"  • Course Units: {CourseUnit.objects.count()}")
print(f"  • Classes: {Class.objects.count()}")
print(f"  • Students: {Student.objects.count()}")
print(f"  • Results: {Result.objects.count()}")
print(f"  • Attendance Records: {AttendanceRecord.objects.count()}")
print(f"  • Invoices: {Invoice.objects.count()}")
print(f"  • Payments: {Payment.objects.count()}")
print(f"  • Financial Clearances: {FinancialClearance.objects.count()}")
print(f"  • Employees: {Employee.objects.count()}")
print(f"  • Timetable Entries: {Timetable.objects.count()}")

print("\n🔑 Login Credentials:")
print("-"*40)
print("  superadmin / Super@2024  → Super Admin")
print("  admin / Admin@2024        → Admin")
print("  registrar / Registrar@2024 → Registrar")
print("  staff / Staff@2024        → Staff")
print("  lecturer / Lecturer@2024  → Lecturer")
print("  finance / Finance@2024    → Finance")
print("  hr / HR@2024              → HR")
print("  student / Student@2024    → Student")
print("-"*40)

print("\n✅ Ready to use!")
print("="*70)
