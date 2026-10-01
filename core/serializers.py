from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Department, Course, CourseCategory, Class, Student, StudentApplication
from finance.models import FeeStructure, Invoice, Payment, FinancialClearance


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'user_type', 'phone', 'profile_picture', 'address', 'is_active']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'user_type', 'phone']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            user_type=validated_data.get('user_type', 'student'),
            phone=validated_data.get('phone', '')
        )
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


# ============================================
# STUDENT SERIALIZER — WITH PROFILE PICTURE FIX
# ============================================
class StudentSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    current_class_name = serializers.CharField(source='current_class.name', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    profile_picture_url = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = [
            'registration_number',
            'enrollment_date',
            'created_at',
            'updated_at',
            'profile_picture_url',
        ]

    def get_profile_picture_url(self, obj):
        """Return an absolute URL for the profile picture, or None."""
        if obj.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
            return obj.profile_picture.url
        return None

    def create(self, validated_data):
        validated_data.pop('user', None)
        validated_data.pop('registration_number', None)
        return Student.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('user', None)
        validated_data.pop('registration_number', None)
        validated_data.pop('enrollment_date', None)

        # Handle profile_picture explicitly so it's never skipped
        if 'profile_picture' in validated_data:
            instance.profile_picture = validated_data.pop('profile_picture')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


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