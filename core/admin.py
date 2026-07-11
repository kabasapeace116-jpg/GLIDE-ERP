from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Department, Course, CourseCategory, Class, Student, StudentApplication

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_active')
    list_filter = ('user_type', 'is_active', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'phone', 'profile_picture', 'address')}),
    )

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'head_of_department')
    search_fields = ('name', 'code')

@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_type')
    list_filter = ('category_type',)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'category', 'department', 'duration', 'tuition_fee', 'is_active')
    list_filter = ('category', 'department', 'duration', 'is_active')
    search_fields = ('name', 'code')

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'course', 'academic_year', 'start_date', 'end_date', 'is_active')
    list_filter = ('course', 'academic_year', 'is_active')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('registration_number', 'full_name', 'course', 'current_class', 'status')
    list_filter = ('status', 'course', 'gender', 'marital_status')
    search_fields = ('registration_number', 'first_name', 'last_name', 'email')

@admin.register(StudentApplication)
class StudentApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'application_id', 
        'full_name_display', 
        'course_type', 
        'program_applied',
        'phone',
        'email',
        'status', 
        'application_date'
    )
    list_filter = ('status', 'course_type', 'application_date')
    search_fields = (
        'application_id', 
        'first_name', 
        'last_name', 
        'full_name', 
        'email', 
        'phone',
        'program_applied',
        'modular_course',
        'diploma_course'
    )
    readonly_fields = ('application_id', 'application_date', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Application Info', {
            'fields': ('application_id', 'application_date', 'course_type', 'status')
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'other_name', 'full_name', 'date_of_birth', 
                       'gender', 'nationality', 'national_id', 'marital_status', 'religion', 'citizenship')
        }),
        ('Contact Information', {
            'fields': ('phone', 'alternate_phone', 'email', 'alternate_email', 'address', 'permanent_address')
        }),
        ('Location', {
            'fields': ('home_district', 'home_parish', 'home_village')
        }),
        ('Program Information', {
            'fields': ('program_applied', 'program_level', 'modular_course', 'diploma_course', 'level_applied')
        }),
        ('Academic Background', {
            'fields': ('academic_background', 'employment_experience')
        }),
        ('UCE Details', {
            'fields': ('uce_index', 'uce_year', 'uce_summary', 'uce_subjects')
        }),
        ('UACE Details', {
            'fields': ('uace_index', 'uace_year', 'uace_overall_grade', 'uace_subjects')
        }),
        ('Other Qualifications', {
            'fields': ('other_qual_from', 'other_qual_to', 'other_qual_institution', 
                       'other_qual_qualification', 'other_qual_class')
        }),
        ('Previous Admission', {
            'fields': ('prev_reg_number', 'prev_institution', 'prev_program')
        }),
        ('Employment', {
            'fields': ('job_position', 'job_employer', 'job_period')
        }),
        ('Guardian/Parent', {
            'fields': ('guardian_relationship', 'guardian_name', 'guardian_nationality', 
                       'guardian_phone', 'guardian_residence')
        }),
        ('Referees', {
            'fields': ('referee1_name', 'referee1_address', 'referee1_phone', 'referee1_email',
                       'referee2_name', 'referee2_address', 'referee2_phone', 'referee2_email')
        }),
        ('Documents', {
            'fields': ('payment_receipt', 'uce_certificate', 'uace_certificate', 'other_qual_certificate')
        }),
        ('Declaration', {
            'fields': ('declaration_signature', 'declaration_date', 'declaration_agreed')
        }),
        ('Review', {
            'fields': ('reviewed_by', 'review_notes', 'interview_date', 'decision_date')
        }),
        ('System', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def full_name_display(self, obj):
        return obj.full_name or f"{obj.first_name} {obj.last_name}".strip()
    full_name_display.short_description = 'Full Name'