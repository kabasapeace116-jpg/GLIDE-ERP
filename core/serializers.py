from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Department, Course, CourseCategory, Class, Student, StudentApplication
from finance.models import FeeStructure, Invoice, Payment, FinancialClearance

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'user_type', 'phone', 'profile_picture', 'address', 'is_active']

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'user_type', 'phone', 'is_active', 'is_staff', 'is_superuser']

    def create(self, validated_data):
        # If password is not provided, generate one
        password = validated_data.pop('password', None)
        if not password:
            import random
            import string
            password = ''.join(random.choices(string.ascii_letters + string.digits + '!@#$%^&*', k=10))
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=password,
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            user_type=validated_data.get('user_type', 'student'),
            phone=validated_data.get('phone', '')
        )
        
        # Set additional fields
        user.is_active = validated_data.get('is_active', True)
        user.is_staff = validated_data.get('is_staff', False)
        user.is_superuser = validated_data.get('is_superuser', False)
        user.save()
        
        # Store password to return it
        setattr(user, '_created_password', password)
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return {'user': user}
        raise serializers.ValidationError("Invalid credentials")

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class CourseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCategory
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = Course
        fields = '__all__'

class ClassSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    
    class Meta:
        model = Class
        fields = '__all__'

class StudentSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    current_class_name = serializers.CharField(source='current_class.name', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    
    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = ['registration_number']
    
    def create(self, validated_data):
        # Remove registration_number if present (will be auto-generated)
        validated_data.pop('registration_number', None)
        
        # Check if user is provided, if not create one
        user_data = validated_data.pop('user', None)
        
        if user_data:
            # If user data is provided (should be an ID), use existing user
            if isinstance(user_data, int):
                try:
                    from core.models import User
                    user = User.objects.get(id=user_data)
                except User.DoesNotExist:
                    user = None
            else:
                user = user_data
        else:
            # Create a user from student data
            from core.models import User
            username = f"{validated_data['first_name'].lower()}.{validated_data['last_name'].lower()}{str(validated_data['phone'])[-4:]}"
            email = validated_data.get('email', f"{username}@glide.edu")
            
            # Check if username already exists, if so add random numbers
            import random
            while User.objects.filter(username=username).exists():
                username = f"{validated_data['first_name'].lower()}.{validated_data['last_name'].lower()}{random.randint(10, 99)}"
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password='Student@2024',  # Default password
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                user_type='student',
                phone=validated_data.get('phone', '')
            )
        
        # Create the student with the user
        student = Student.objects.create(user=user, **validated_data)
        return student
    
    def update(self, instance, validated_data):
        # Remove fields that shouldn't be updated
        validated_data.pop('user', None)
        validated_data.pop('registration_number', None)
        
        return super().update(instance, validated_data)

class StudentApplicationSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course_applied.name', read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentApplication
        fields = '__all__'
    
    def get_full_name(self, obj):
        return obj.full_name or f"{obj.first_name} {obj.last_name}".strip()
    

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