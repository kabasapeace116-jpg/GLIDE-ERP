from django.contrib import admin
from .models import AdmissionBatch, AdmittedStudent, AcademicYear, Semester

@admin.register(AdmissionBatch)
class AdmissionBatchAdmin(admin.ModelAdmin):
    list_display = ('name', 'academic_year', 'start_date', 'end_date', 'is_active')

@admin.register(AdmittedStudent)
class AdmittedStudentAdmin(admin.ModelAdmin):
    list_display = ('student', 'admission_batch', 'admission_date', 'confirmed_enrollment')
    list_filter = ('admission_batch', 'confirmed_enrollment')

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_current')

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('academic_year', 'name', 'start_date', 'end_date', 'is_current')
    list_filter = ('academic_year', 'is_current')