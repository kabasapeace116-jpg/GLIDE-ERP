from django.db import models
from core.models import Student, Course, User
from django.utils import timezone

class AdmissionBatch(models.Model):
    name = models.CharField(max_length=100)
    academic_year = models.CharField(max_length=20)
    semester = models.CharField(max_length=10, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.academic_year})"

class AdmittedStudent(models.Model):
    application = models.ForeignKey('core.StudentApplication', on_delete=models.CASCADE, related_name='admitted_students')
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='admission_record')
    admission_batch = models.ForeignKey(AdmissionBatch, on_delete=models.SET_NULL, null=True)
    admission_date = models.DateField(auto_now_add=True)
    admission_letter_sent = models.BooleanField(default=False)
    admission_letter_date = models.DateField(null=True, blank=True)
    confirmed_enrollment = models.BooleanField(default=False)
    confirmed_enrollment_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Admission - {self.student.registration_number}"

class AcademicYear(models.Model):
    name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.is_current:
            AcademicYear.objects.filter(is_current=True).update(is_current=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Semester(models.Model):
    SEMESTER_TYPES = (
        ('semester1', 'Semester 1'),
        ('semester2', 'Semester 2'),
        ('semester3', 'Semester 3'),
        ('trimester1', 'Trimester 1'),
        ('trimester2', 'Trimester 2'),
        ('trimester3', 'Trimester 3'),
    )
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='semesters')
    name = models.CharField(max_length=20, choices=SEMESTER_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    registration_deadline = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.is_current:
            Semester.objects.filter(is_current=True).update(is_current=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_name_display()} - {self.academic_year.name}"