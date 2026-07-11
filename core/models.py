from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    USER_TYPES = (
        ('super_admin', 'Super Admin'),
        ('admin', 'Administrator'),
        ('staff', 'Staff'),
        ('lecturer', 'Lecturer'),
        ('student', 'Student'),
        ('finance', 'Finance Officer'),
        ('registrar', 'Registrar'),
        ('hr', 'HR Officer'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='student')
    phone = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    address = models.TextField(blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.username} - {self.get_user_type_display()}"

    def is_super_admin(self):
        return self.user_type == 'super_admin' or self.is_superuser

    def is_admin_staff(self):
        return self.user_type in ['super_admin', 'admin', 'registrar']

    def is_finance(self):
        return self.user_type == 'finance'

    def is_lecturer(self):
        return self.user_type == 'lecturer'

    def is_student(self):
        return self.user_type == 'student'

    def is_hr(self):
        return self.user_type == 'hr'


class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    head_of_department = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='heading_department')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class CourseCategory(models.Model):
    CATEGORY_TYPES = (
        ('diploma', 'Diploma'),
        ('certificate', 'Ordinary Certificate'),
        ('occupational', 'Occupational Certificate'),
        ('modular', 'Modular Training'),
        ('driving', 'Driving Training'),
    )
    name = models.CharField(max_length=50)
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"


class Course(models.Model):
    DURATION_CHOICES = (
        ('1_month', '1 Month'),
        ('2_weeks', '2 Weeks'),
        ('1_week', '1 Week'),
        ('1_year', '1 Year'),
        ('2_years', '2 Years'),
        ('3_years', '3 Years'),
    )
    LEVEL_CHOICES = (
        ('level1', 'Level 1'),
        ('level2', 'Level 2'),
        ('level3', 'Level 3'),
        ('level4', 'Level 4'),
        ('level5', 'Level 5'),
    )
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE, related_name='courses')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    duration = models.CharField(max_length=20, choices=DURATION_CHOICES)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, blank=True)
    entry_requirements = models.TextField()
    description = models.TextField()
    tuition_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    application_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Class(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='classes')
    academic_year = models.CharField(max_length=20)
    semester = models.CharField(max_length=10, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    capacity = models.IntegerField(default=30)
    current_enrollment = models.IntegerField(default=0)
    class_teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='class_teacher')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = f"CLS-{self.name[:4].upper()}-{self.academic_year[:4]}"
        super().save(*args, **kwargs)


class Student(models.Model):
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )
    MARITAL_STATUS = (
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
        ('other', 'Other'),
    )
    STUDENT_STATUS = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('graduated', 'Graduated'),
        ('dropped', 'Dropped'),
        ('suspended', 'Suspended'),
    )
    registration_number = models.CharField(max_length=20, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    other_name = models.CharField(max_length=50, blank=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    nationality = models.CharField(max_length=50, default='Ugandan')
    national_id = models.CharField(max_length=20, blank=True)
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS, default='single')
    religion = models.CharField(max_length=50, blank=True)
    current_class = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, related_name='students')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='students')
    enrollment_date = models.DateField(auto_now_add=True)
    graduation_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STUDENT_STATUS, default='active')
    phone = models.CharField(max_length=15)
    alternate_phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField()
    address = models.TextField()
    district = models.CharField(max_length=50, blank=True)
    county = models.CharField(max_length=50, blank=True)
    sub_county = models.CharField(max_length=50, blank=True)
    parish = models.CharField(max_length=50, blank=True)
    village = models.CharField(max_length=50, blank=True)
    profile_picture = models.ImageField(upload_to='students/', null=True, blank=True)
    sponsor_type = models.CharField(max_length=50, blank=True)
    parent_name = models.CharField(max_length=100, blank=True)
    parent_phone = models.CharField(max_length=15, blank=True)
    parent_address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    registration_number = models.CharField(max_length=20, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.registration_number:
            year = timezone.now().year
            course_code = self.course.code[:4].upper()
            last_student = Student.objects.filter(
                registration_number__startswith=f"GLIDE/{year}/{course_code}"
            ).order_by('-registration_number').first()
            if last_student:
                seq = int(last_student.registration_number.split('/')[-1]) + 1
            else:
                seq = 1
            self.registration_number = f"GLIDE/{year}/{course_code}/{seq:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.registration_number} - {self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name} {self.other_name}".strip()


class StudentApplication(models.Model):
    APPLICATION_STATUS = (
        ('pending', 'Pending'),
        ('reviewing', 'Reviewing'),
        ('interview', 'Interview Scheduled'),
        ('admitted', 'Admitted'),
        ('rejected', 'Rejected'),
        ('waitlisted', 'Waitlisted'),
    )
    STUDENT_CATEGORY = (
        ('occupational', 'Occupational Certificate'),
        ('modular', 'Modular Training'),
        ('diploma', 'Diploma'),
    )
    
    # Application Info
    application_id = models.CharField(max_length=20, unique=True)
    course_type = models.CharField(max_length=20, choices=STUDENT_CATEGORY, blank=True)
    application_date = models.DateField(auto_now_add=True)
    
    # Personal Information
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    other_name = models.CharField(max_length=50, blank=True)
    full_name = models.CharField(max_length=200, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=(('male','Male'),('female','Female'),('other','Other')), blank=True)
    nationality = models.CharField(max_length=50, default='Ugandan', blank=True)
    national_id = models.CharField(max_length=20, blank=True)
    marital_status = models.CharField(max_length=20, blank=True)
    religion = models.CharField(max_length=50, blank=True)
    citizenship = models.CharField(max_length=50, blank=True)
    
    # Contact Information
    phone = models.CharField(max_length=15, blank=True)
    alternate_phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    alternate_email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    permanent_address = models.TextField(blank=True)
    
    # Location
    district = models.CharField(max_length=50, blank=True)
    county = models.CharField(max_length=50, blank=True)
    sub_county = models.CharField(max_length=50, blank=True)
    parish = models.CharField(max_length=50, blank=True)
    village = models.CharField(max_length=50, blank=True)
    home_district = models.CharField(max_length=50, blank=True)
    home_parish = models.CharField(max_length=50, blank=True)
    home_village = models.CharField(max_length=50, blank=True)
    
    # Program Information
    program_applied = models.CharField(max_length=200, blank=True)
    program_level = models.CharField(max_length=50, blank=True)
    modular_course = models.CharField(max_length=200, blank=True)
    diploma_course = models.CharField(max_length=200, blank=True)
    level_applied = models.CharField(max_length=20, blank=True)
    
    # Academic Background
    academic_background = models.TextField(blank=True)
    employment_experience = models.TextField(blank=True)
    
    # UCE Details
    uce_index = models.CharField(max_length=20, blank=True)
    uce_year = models.CharField(max_length=10, blank=True)
    uce_summary = models.CharField(max_length=50, blank=True)
    uce_subjects = models.JSONField(default=dict, blank=True)
    
    # UACE Details
    uace_index = models.CharField(max_length=20, blank=True)
    uace_year = models.CharField(max_length=10, blank=True)
    uace_overall_grade = models.CharField(max_length=5, blank=True)
    uace_subjects = models.JSONField(default=dict, blank=True)
    
    # Other Qualifications
    other_qual_from = models.CharField(max_length=10, blank=True)
    other_qual_to = models.CharField(max_length=10, blank=True)
    other_qual_institution = models.CharField(max_length=200, blank=True)
    other_qual_qualification = models.CharField(max_length=200, blank=True)
    other_qual_class = models.CharField(max_length=100, blank=True)
    
    # Previous Admission
    prev_reg_number = models.CharField(max_length=50, blank=True)
    prev_institution = models.CharField(max_length=200, blank=True)
    prev_program = models.CharField(max_length=200, blank=True)
    
    # Employment
    job_position = models.CharField(max_length=200, blank=True)
    job_employer = models.CharField(max_length=200, blank=True)
    job_period = models.CharField(max_length=50, blank=True)
    
    # Guardian/Parent
    guardian_relationship = models.CharField(max_length=50, blank=True)
    guardian_name = models.CharField(max_length=200, blank=True)
    guardian_nationality = models.CharField(max_length=50, blank=True)
    guardian_phone = models.CharField(max_length=20, blank=True)
    guardian_residence = models.TextField(blank=True)
    
    # Referees
    referee1_name = models.CharField(max_length=200, blank=True)
    referee1_address = models.TextField(blank=True)
    referee1_phone = models.CharField(max_length=20, blank=True)
    referee1_email = models.EmailField(blank=True)
    
    referee2_name = models.CharField(max_length=200, blank=True)
    referee2_address = models.TextField(blank=True)
    referee2_phone = models.CharField(max_length=20, blank=True)
    referee2_email = models.EmailField(blank=True)
    
    # Documents
    payment_receipt = models.FileField(upload_to='applications/receipts/', null=True, blank=True)
    uce_certificate = models.FileField(upload_to='applications/uce/', null=True, blank=True)
    uace_certificate = models.FileField(upload_to='applications/uace/', null=True, blank=True)
    other_qual_certificate = models.FileField(upload_to='applications/other_qual/', null=True, blank=True)
    
    # Declaration
    declaration_signature = models.CharField(max_length=100, blank=True)
    declaration_date = models.DateField(null=True, blank=True)
    declaration_agreed = models.BooleanField(default=False)
    
    # System Fields
    status = models.CharField(max_length=20, choices=APPLICATION_STATUS, default='pending')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    review_notes = models.TextField(blank=True)
    interview_date = models.DateTimeField(null=True, blank=True)
    decision_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.application_id:
            year = timezone.now().year
            last_app = StudentApplication.objects.filter(
                application_id__startswith=f"APP/{year}"
            ).order_by('-application_id').first()
            if last_app:
                seq = int(last_app.application_id.split('/')[-1]) + 1
            else:
                seq = 1
            self.application_id = f"APP/{year}/{seq:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.application_id} - {self.full_name or self.first_name} {self.last_name}"