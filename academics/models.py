from django.db import models
from core.models import Course, Class, Student, User
from admissions.models import Semester, AcademicYear
from django.utils import timezone

class CourseUnit(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='units')
    credit_hours = models.IntegerField(default=3)
    description = models.TextField(blank=True)
    is_core = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

class Timetable(models.Model):
    DAY_CHOICES = (
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    )
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='timetables')
    course_unit = models.ForeignKey(CourseUnit, on_delete=models.CASCADE, related_name='timetables')
    lecturer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='timetables', limit_choices_to={'user_type': 'lecturer'})
    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    venue = models.CharField(max_length=100)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='timetables')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.class_obj.name} - {self.course_unit.code} ({self.day_of_week} {self.start_time})"

class Assessment(models.Model):
    ASSESSMENT_TYPES = (
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
        ('midterm', 'Midterm Exam'),
        ('final', 'Final Exam'),
        ('practical', 'Practical'),
        ('project', 'Project'),
        ('continuous', 'Continuous Assessment'),
    )
    name = models.CharField(max_length=200)
    course_unit = models.ForeignKey(CourseUnit, on_delete=models.CASCADE, related_name='assessments')
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='assessments')
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPES)
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=20)
    date = models.DateField()
    duration_minutes = models.IntegerField(default=60)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='assessments')
    is_published = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.course_unit.code} ({self.get_assessment_type_display()})"

class Result(models.Model):
    GRADING_SCALE = (
        ('A', 'A - Outstanding'),
        ('B+', 'B+ - Very Good'),
        ('B', 'B - Good'),
        ('C+', 'C+ - Average'),
        ('C', 'C - Satisfactory'),
        ('D', 'D - Pass'),
        ('F', 'F - Fail'),
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='results')
    course_unit = models.ForeignKey(CourseUnit, on_delete=models.CASCADE, related_name='results')
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='results')
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    grade = models.CharField(max_length=5, choices=GRADING_SCALE, blank=True)
    remarks = models.TextField(blank=True)
    entered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='entered_results')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='results')
    is_published = models.BooleanField(default=False)
    published_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.score is not None:
            if self.score >= 80:
                self.grade = 'A'
            elif self.score >= 70:
                self.grade = 'B+'
            elif self.score >= 60:
                self.grade = 'B'
            elif self.score >= 50:
                self.grade = 'C+'
            elif self.score >= 40:
                self.grade = 'C'
            elif self.score >= 35:
                self.grade = 'D'
            else:
                self.grade = 'F'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.registration_number} - {self.course_unit.code} - {self.grade}"

class StudentCourseProgress(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='course_progress')
    course_unit = models.ForeignKey(CourseUnit, on_delete=models.CASCADE, related_name='student_progress')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='student_progress')
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    grade = models.CharField(max_length=5, blank=True)
    is_completed = models.BooleanField(default=False)
    is_retake = models.BooleanField(default=False)
    is_passed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.registration_number} - {self.course_unit.code} - {self.grade}"

class AttendanceRecord(models.Model):
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='attendance_records')
    course_unit = models.ForeignKey(CourseUnit, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    time_in = models.TimeField(null=True, blank=True)
    time_out = models.TimeField(null=True, blank=True)
    remarks = models.TextField(blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'course_unit', 'date')

    def __str__(self):
        return f"{self.student.registration_number} - {self.date} - {self.status}"