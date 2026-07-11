"""
GLIDE Institute - Complete Student Seed Data Script (FIXED)
"""

import os
import sys
import django
from datetime import date, timedelta, datetime
from django.db import IntegrityError
from decimal import Decimal
import random

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glide_sms.settings')
django.setup()

from core.models import User, Department, Course, CourseCategory, Class, Student, StudentApplication
from admissions.models import AcademicYear, Semester, AdmissionBatch, AdmittedStudent
from academics.models import CourseUnit, Assessment, Result, StudentCourseProgress, AttendanceRecord
from finance.models import FeeStructure, Invoice, Payment, FinancialClearance

print("="*70)
print("GLIDE INSTITUTE - STUDENT SEED DATA GENERATOR")
print("="*70)

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
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)

def random_phone():
    return f"077{random.randint(100000, 999999)}"

def random_grade():
    weights = ['A'] * 15 + ['B+'] * 20 + ['B'] * 25 + ['C+'] * 20 + ['C'] * 15 + ['D'] * 4 + ['F'] * 1
    return random.choice(weights)

def grade_to_score(grade):
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

# ============================================
# 1. GET OR CREATE DEPARTMENTS
# ============================================
print("\n📚 Setting up departments...")

departments_data = [
    {'name': 'Engineering', 'code': 'ENG'},
    {'name': 'Business Studies', 'code': 'BUS'},
    {'name': 'Information Technology', 'code': 'ICT'},
    {'name': 'Agriculture', 'code': 'AGR'},
    {'name': 'Hospitality', 'code': 'HOS'},
]

departments = {}
for dept_data in departments_data:
    dept, created = Department.objects.get_or_create(
        code=dept_data['code'],
        defaults={'name': dept_data['name']}
    )
    departments[dept.code] = dept
    print(f"  {'✅' if created else '⚠️'} {dept.name} ({dept.code})")

# ============================================
# 2. GET OR CREATE COURSE CATEGORIES
# ============================================
print("\n📚 Setting up course categories...")

categories_data = [
    {'name': 'Diploma', 'category_type': 'diploma'},
    {'name': 'Certificate', 'category_type': 'certificate'},
    {'name': 'Occupational', 'category_type': 'occupational'},
    {'name': 'Modular', 'category_type': 'modular'},
]

categories = {}
for cat_data in categories_data:
    cat, created = CourseCategory.objects.get_or_create(
        category_type=cat_data['category_type'],
        defaults={'name': cat_data['name']}
    )
    categories[cat.category_type] = cat
    print(f"  {'✅' if created else '⚠️'} {cat.name} ({cat.category_type})")

# ============================================
# 3. GET OR CREATE COURSES
# ============================================
print("\n📚 Setting up courses...")

courses_data = [
    {
        'name': 'Diploma in Information Technology',
        'code': 'DIT',
        'category_type': 'diploma',
        'department_code': 'ICT',
        'duration': '2_years',
        'entry_requirements': 'UACE with at least 1 Principal Pass',
        'tuition_fee': 2500000,
        'application_fee': 50000
    },
    {
        'name': 'Diploma in Business Administration',
        'code': 'DBA',
        'category_type': 'diploma',
        'department_code': 'BUS',
        'duration': '2_years',
        'entry_requirements': 'UACE with at least 1 Principal Pass',
        'tuition_fee': 2200000,
        'application_fee': 50000
    },
    {
        'name': 'Diploma in Mechanical Engineering',
        'code': 'DME',
        'category_type': 'diploma',
        'department_code': 'ENG',
        'duration': '2_years',
        'entry_requirements': 'UACE with at least 1 Principal Pass',
        'tuition_fee': 2800000,
        'application_fee': 50000
    },
    {
        'name': 'Diploma in Electrical Engineering',
        'code': 'DEE',
        'category_type': 'diploma',
        'department_code': 'ENG',
        'duration': '2_years',
        'entry_requirements': 'UACE with at least 1 Principal Pass',
        'tuition_fee': 2700000,
        'application_fee': 50000
    },
    {
        'name': 'Certificate in Information Technology',
        'code': 'CIT',
        'category_type': 'certificate',
        'department_code': 'ICT',
        'duration': '2_years',
        'entry_requirements': 'UCE with at least 5 Passes',
        'tuition_fee': 1500000,
        'application_fee': 50000
    },
    {
        'name': 'Certificate in Business Administration',
        'code': 'CBA',
        'category_type': 'certificate',
        'department_code': 'BUS',
        'duration': '2_years',
        'entry_requirements': 'UCE with at least 5 Passes',
        'tuition_fee': 1300000,
        'application_fee': 50000
    },
    {
        'name': 'Motor Vehicle Repair and Maintenance',
        'code': 'MVR',
        'category_type': 'occupational',
        'department_code': 'ENG',
        'duration': '2_years',
        'entry_requirements': 'UCE Certificate',
        'tuition_fee': 1200000,
        'application_fee': 30000
    },
    {
        'name': 'Tailoring and Garment Design',
        'code': 'TGD',
        'category_type': 'occupational',
        'department_code': 'BUS',
        'duration': '2_years',
        'entry_requirements': 'UCE Certificate',
        'tuition_fee': 1000000,
        'application_fee': 30000
    },
]

courses = {}
for course_data in courses_data:
    try:
        category = categories.get(course_data['category_type'])
        dept = departments.get(course_data['department_code'])
        if category and dept:
            course, created = Course.objects.get_or_create(
                code=course_data['code'],
                defaults={
                    'name': course_data['name'],
                    'category': category,
                    'department': dept,
                    'duration': course_data['duration'],
                    'entry_requirements': course_data['entry_requirements'],
                    'tuition_fee': course_data['tuition_fee'],
                    'application_fee': course_data['application_fee'],
                    'is_active': True
                }
            )
            courses[course.code] = course
            print(f"  {'✅' if created else '⚠️'} {course.name} ({course.code})")
    except Exception as e:
        print(f"  ❌ Error creating {course_data['code']}: {e}")

# ============================================
# 4. GET OR CREATE CLASSES FOR EACH COURSE
# ============================================
print("\n📚 Creating classes for each course...")

course_classes = {}
for course_code, course in courses.items():
    class_obj, created = Class.objects.get_or_create(
        code=f"CLS-{course_code}-2024",
        defaults={
            'name': f"{course.name} - Year 1",
            'course': course,
            'academic_year': ACADEMIC_YEAR,
            'semester': SEMESTER,
            'start_date': date(2024, 8, 1),
            'end_date': date(2024, 12, 15),
            'capacity': 50,
            'current_enrollment': 0,
            'is_active': True
        }
    )
    course_classes[course_code] = class_obj
    print(f"  {'✅' if created else '⚠️'} Class created for {course.name}")

# ============================================
# 5. GET OR CREATE ACADEMIC YEAR & SEMESTER
# ============================================
print("\n📚 Setting up academic year...")

academic_year, created = AcademicYear.objects.get_or_create(
    name=ACADEMIC_YEAR,
    defaults={
        'start_date': date(2024, 8, 1),
        'end_date': date(2025, 7, 31),
        'is_current': True
    }
)
print(f"  {'✅' if created else '⚠️'} {academic_year.name}")

semester, created = Semester.objects.get_or_create(
    academic_year=academic_year,
    name=SEMESTER,
    defaults={
        'start_date': date(2024, 8, 1),
        'end_date': date(2024, 12, 15),
        'is_current': True,
        'registration_deadline': date(2024, 8, 15)
    }
)
print(f"  {'✅' if created else '⚠️'} {semester.get_name_display()}")

# ============================================
# 6. CREATE COURSE UNITS
# ============================================
print("\n📚 Creating course units...")

course_units = {}
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
            unit, created = CourseUnit.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'course': course,
                    'credit_hours': credits,
                    'is_core': True
                }
            )
            course_units[code] = unit
            print(f"  {'✅' if created else '⚠️'} {code} - {name}")

# ============================================
# 7. CREATE FEE STRUCTURES
# ============================================
print("\n📚 Creating fee structures...")

fee_types = ['tuition', 'application', 'exam', 'library', 'activity']
for course in courses.values():
    for fee_type in fee_types:
        amount = course.tuition_fee if fee_type == 'tuition' else random.randint(30000, 150000)
        FeeStructure.objects.get_or_create(
            course=course,
            fee_type=fee_type,
            academic_year=ACADEMIC_YEAR,
            defaults={
                'amount': amount,
                'is_required': True,
                'is_active': True
            }
        )
    print(f"  ✅ Fee structures created for {course.name}")

# ============================================
# 8. CREATE STUDENTS
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

created_students = []
failed_students = []

for i in range(STUDENT_COUNT):
    try:
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        username = f"{first_name.lower()}.{last_name.lower()}{random.randint(10, 99)}"
        email = f"{username}@glide.edu"
        gender = random.choice(gender_options)
        dob = random_date(date(1995, 1, 1), date(2005, 12, 31))
        
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
        
        # Assign course and get its class
        course_code, course = random.choice(course_list)
        class_obj = course_classes.get(course_code)
        
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
            current_class=class_obj,  # Assign the class
            status=random.choice(status_options),
            phone=random_phone(),
            email=email,
            address=f"{random.randint(1, 100)} Kampala Road",
            district=random.choice(['Kampala', 'Wakiso', 'Mukono', 'Jinja', 'Butaleja', 'Tororo', 'Mbale']),
            village=random.choice(['Kampala', 'Ntinda', 'Bukoto', 'Naguru', 'Muyenga', 'Kiwatule']),
            parent_name=f"{random.choice(['Mr.', 'Mrs.'])} {random.choice(last_names)}",
            parent_phone=random_phone()
        )
        
        # Update class enrollment count
        if class_obj:
            class_obj.current_enrollment += 1
            class_obj.save()
        
        created_students.append(student.registration_number)
        print(f"  ✅ {i+1}. {student.registration_number} - {student.full_name} ({course.name})")
        
        # ============================================
        # 9. CREATE APPLICATION
        # ============================================
        app_id = f"APP/2024/{i+1:04d}"
        
        app, app_created = StudentApplication.objects.get_or_create(
            application_id=app_id,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone': random_phone(),
                'course_type': course.category.category_type if course.category else 'diploma',
                'program_applied': course.name,
                'status': 'admitted',
                'application_date': random_date(date(2024, 6, 1), date(2024, 7, 31)),
                'declaration_agreed': True,
                'declaration_signature': f"{first_name} {last_name}",
                'declaration_date': random_date(date(2024, 6, 1), date(2024, 7, 31))
            }
        )
        
        # ============================================
        # 10. CREATE ADMISSION RECORD
        # ============================================
        admitted, adm_created = AdmittedStudent.objects.get_or_create(
            student=student,
            defaults={
                'application': app,
                'admission_date': random_date(date(2024, 7, 1), date(2024, 8, 31)),
                'confirmed_enrollment': True,
                'confirmed_enrollment_date': random_date(date(2024, 8, 1), date(2024, 8, 15))
            }
        )
        
        # ============================================
        # 11. CREATE ACADEMIC PROGRESS & RESULTS
        # ============================================
        course_units_list = CourseUnit.objects.filter(course=course)
        
        for unit in course_units_list:
            grade = random_grade()
            score = grade_to_score(grade)
            is_passed = grade != 'F'
            
            # Create course progress
            progress, _ = StudentCourseProgress.objects.get_or_create(
                student=student,
                course_unit=unit,
                semester=semester,
                defaults={
                    'score': score,
                    'grade': grade,
                    'is_completed': True,
                    'is_retake': False,
                    'is_passed': is_passed
                }
            )
            
            # Create assessment with class_obj (FIXED)
            assessment, _ = Assessment.objects.get_or_create(
                course_unit=unit,
                name=f"{unit.name} - Final Exam",
                defaults={
                    'class_obj': class_obj,  # Now we have a class_obj
                    'assessment_type': 'final',
                    'max_score': 100,
                    'weight': 50,
                    'date': random_date(date(2024, 11, 1), date(2024, 12, 10)),
                    'duration_minutes': 120,
                    'semester': semester,
                    'is_published': True,
                    'is_closed': True
                }
            )
            
            Result.objects.create(
                student=student,
                course_unit=unit,
                assessment=assessment,
                score=score,
                grade=grade,
                semester=semester,
                is_published=True,
                published_date=random_date(date(2024, 12, 1), date(2024, 12, 15))
            )
        
        # ============================================
        # 12. CREATE ATTENDANCE RECORDS
        # ============================================
        start_date = date(2024, 8, 15)
        end_date = date(2024, 11, 30)
        current_date = start_date
        
        attendance_statuses = ['present'] * 70 + ['absent'] * 10 + ['late'] * 15 + ['excused'] * 5
        
        while current_date <= end_date:
            if current_date.weekday() < 5:
                for unit in course_units_list[:3]:
                    status = random.choice(attendance_statuses)
                    AttendanceRecord.objects.create(
                        student=student,
                        class_obj=class_obj,
                        course_unit=unit,
                        date=current_date,
                        status=status,
                        time_in=random.choice([None, '08:00', '08:15', '08:30', '09:00']),
                        time_out=random.choice([None, '16:00', '16:30', '17:00'])
                    )
            current_date += timedelta(days=1)
        
        # ============================================
        # 13. CREATE FINANCIAL RECORDS
        # ============================================
        fee_structures = FeeStructure.objects.filter(course=course, academic_year=ACADEMIC_YEAR)
        total_fee = sum(f.amount for f in fee_structures)
        
        invoice, _ = Invoice.objects.get_or_create(
            student=student,
            semester=semester,
            defaults={
                'invoice_number': f"INV/{ACADEMIC_YEAR[:4]}/{student.id:04d}",
                'issue_date': random_date(date(2024, 8, 1), date(2024, 8, 10)),
                'due_date': random_date(date(2024, 9, 1), date(2024, 9, 30)),
                'total_amount': total_fee,
                'status': 'fully_paid' if random.random() > 0.2 else 'partially_paid'
            }
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
        
        if random.random() < 0.8:
            FinancialClearance.objects.create(
                student=student,
                semester=semester,
                is_cleared=True,
                clearance_date=random_date(date(2024, 9, 1), date(2024, 10, 15)),
                notes="Cleared - All fees paid"
            )
        else:
            FinancialClearance.objects.create(
                student=student,
                semester=semester,
                is_cleared=False,
                notes="Pending payment"
            )
            
    except IntegrityError as e:
        failed_students.append(f"{first_name} {last_name}")
        print(f"  ❌ Failed to create student {first_name} {last_name}: {e}")
    except Exception as e:
        failed_students.append(f"{first_name} {last_name}")
        print(f"  ❌ Error creating student {first_name} {last_name}: {e}")

# ============================================
# 14. FINAL SUMMARY
# ============================================
print("\n" + "="*70)
print("SEED DATA COMPLETE!")
print("="*70)

total_students = Student.objects.count()
total_courses = Course.objects.count()
total_results = Result.objects.count()
total_attendance = AttendanceRecord.objects.count()
total_invoices = Invoice.objects.count()
total_payments = Payment.objects.count()
total_clearance = FinancialClearance.objects.count()

print("\n📊 Summary:")
print(f"  • Students Created: {len(created_students)}")
print(f"  • Total Students: {total_students}")
print(f"  • Total Courses: {total_courses}")
print(f"  • Total Results: {total_results}")
print(f"  • Total Attendance Records: {total_attendance}")
print(f"  • Total Invoices: {total_invoices}")
print(f"  • Total Payments: {total_payments}")
print(f"  • Total Financial Clearances: {total_clearance}")

if failed_students:
    print(f"  ❌ Failed: {len(failed_students)} students")

print("\n📊 Performance Statistics:")
from academics.models import StudentCourseProgress
all_progress = StudentCourseProgress.objects.all()
grade_points = {'A': 5, 'B+': 4.5, 'B': 4, 'C+': 3.5, 'C': 3, 'D': 2, 'F': 0}
total_pts = 0
total_units = 0
for prog in all_progress:
    if prog.grade in grade_points:
        total_pts += grade_points[prog.grade]
        total_units += 1
avg_gpa = round(total_pts / total_units, 2) if total_units > 0 else 0
print(f"  • Average GPA: {avg_gpa}")

passed = all_progress.filter(is_passed=True).count()
total_progress = all_progress.count()
pass_rate = round((passed / total_progress) * 100, 1) if total_progress > 0 else 0
print(f"  • Pass Rate: {pass_rate}%")

print(f"\n📊 Financial Summary:")
total_revenue = Payment.objects.aggregate(total=models.Sum('amount'))['total'] or 0
total_outstanding = Invoice.objects.aggregate(total=models.Sum('balance'))['total'] or 0
print(f"  • Total Revenue: UGX {total_revenue:,.2f}")
print(f"  • Outstanding Balance: UGX {total_outstanding:,.2f}")

print(f"\n📊 Attendance Summary:")
total_attendance = AttendanceRecord.objects.count()
present = AttendanceRecord.objects.filter(status='present').count()
absent = AttendanceRecord.objects.filter(status='absent').count()
late = AttendanceRecord.objects.filter(status='late').count()
attendance_rate = round((present / total_attendance) * 100, 1) if total_attendance > 0 else 0
print(f"  • Total Records: {total_attendance}")
print(f"  • Present: {present}")
print(f"  • Absent: {absent}")
print(f"  • Late: {late}")
print(f"  • Attendance Rate: {attendance_rate}%")

print("\n" + "="*70)
print("✅ Seed data generation complete!")
print("="*70)