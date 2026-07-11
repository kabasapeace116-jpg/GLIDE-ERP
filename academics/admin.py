from django.contrib import admin
from .models import CourseUnit, Timetable, Assessment, Result, StudentCourseProgress, AttendanceRecord

@admin.register(CourseUnit)
class CourseUnitAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'course', 'credit_hours', 'is_core')
    list_filter = ('course', 'is_core')
    search_fields = ('code', 'name')

@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('class_obj', 'course_unit', 'day_of_week', 'start_time', 'end_time', 'venue')
    list_filter = ('day_of_week', 'class_obj', 'semester')

@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'course_unit', 'class_obj', 'assessment_type', 'date', 'is_published')
    list_filter = ('assessment_type', 'class_obj', 'semester')

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'course_unit', 'score', 'grade', 'semester', 'is_published')
    list_filter = ('semester', 'grade', 'is_published')
    search_fields = ('student__registration_number', 'student__first_name', 'student__last_name')

@admin.register(StudentCourseProgress)
class StudentCourseProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'course_unit', 'score', 'grade', 'is_completed', 'is_retake')
    list_filter = ('is_completed', 'is_retake', 'semester')

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'course_unit', 'date', 'status')
    list_filter = ('status', 'date', 'class_obj')