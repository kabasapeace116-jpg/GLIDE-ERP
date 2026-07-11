from rest_framework import serializers
from .models import FeeStructure, Invoice, Payment, FinancialClearance

# Import models from core (not from finance.models)
from core.models import User, Department, Course, CourseCategory, Class, Student, StudentApplication

class FeeStructureSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    
    class Meta:
        model = FeeStructure
        fields = '__all__'

class InvoiceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    
    class Meta:
        model = Invoice
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    
    class Meta:
        model = Payment
        fields = '__all__'

class FinancialClearanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    
    class Meta:
        model = FinancialClearance
        fields = '__all__'