from rest_framework import serializers
from .models import AdmissionBatch, AdmittedStudent, AcademicYear, Semester
from core.serializers import StudentSerializer, StudentApplicationSerializer

class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = '__all__'

class SemesterSerializer(serializers.ModelSerializer):
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    
    class Meta:
        model = Semester
        fields = '__all__'

class AdmissionBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionBatch
        fields = '__all__'

class AdmittedStudentSerializer(serializers.ModelSerializer):
    student_details = StudentSerializer(source='student', read_only=True)
    application_details = StudentApplicationSerializer(source='application', read_only=True)
    
    class Meta:
        model = AdmittedStudent
        fields = '__all__'