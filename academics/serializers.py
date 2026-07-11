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