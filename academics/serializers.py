from rest_framework import serializers
from .models import CourseUnit, Timetable, Assessment, Result, StudentCourseProgress, AttendanceRecord
from core.serializers import StudentSerializer

class CourseUnitSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    
    class Meta:
        model = CourseUnit
        fields = '__all__'

class TimetableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timetable
        fields = '__all__'

class AssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = '__all__'

class ResultSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    course_unit_name = serializers.CharField(source='course_unit.name', read_only=True)
    
    class Meta:
        model = Result
        fields = '__all__'

class StudentCourseProgressSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    course_unit_name = serializers.CharField(source='course_unit.name', read_only=True)
    
    class Meta:
        model = StudentCourseProgress
        fields = '__all__'

class AttendanceRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    
    class Meta:
        model = AttendanceRecord
        fields = '__all__'

from .models import Certificate


class CertificateSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_registration = serializers.CharField(
        source='student.registration_number', read_only=True
    )
    certificate_type_display = serializers.CharField(
        source='get_certificate_type_display', read_only=True
    )
    issued_by_name = serializers.CharField(
        source='issued_by.get_full_name', read_only=True
    )

    class Meta:
        model = Certificate
        fields = '__all__'
        read_only_fields = (
            'certificate_number', 'verification_code',
            'snapshot_data', 'created_at', 'updated_at',
        )