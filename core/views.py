from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
# REMOVED ALL JWT IMPORTS
# from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.shortcuts import redirect, render
from django.contrib import messages
from django.db.models import Q, Sum
from django.utils import timezone
from datetime import timedelta
import json
import random
import string

User = get_user_model()

from .models import (
    User, Department, Course, CourseCategory, Class, Student, StudentApplication
)
from .serializers import (
    UserSerializer, UserCreateSerializer, LoginSerializer, 
    DepartmentSerializer, CourseSerializer, CourseCategorySerializer,
    ClassSerializer, StudentSerializer, StudentApplicationSerializer,
    InvoiceSerializer, PaymentSerializer
)
from .permissions import IsAdmin, IsStaff, IsStudent, IsFinance

# Import models from other apps
from admissions.models import AcademicYear, Semester, AdmissionBatch, AdmittedStudent
from academics.models import CourseUnit, Assessment, Result, StudentCourseProgress, AttendanceRecord
from finance.models import FeeStructure, Invoice, Payment, FinancialClearance


class AuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    
    @method_decorator(csrf_exempt)
    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        print("=" * 50)
        print("LOGIN ATTEMPT")
        print(f"Request data: {request.data}")
        
        try:
            serializer = LoginSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.validated_data['user']
                print(f"User found: {user.username} (Type: {user.user_type})")
                
                # Login the user for session-based auth
                auth_login(request, user)
                request.session.save()
                print(f"Session key: {request.session.session_key}")
                
                # Determine redirect URL based on user type
                redirect_url = '/dashboard/student/'
                if user.user_type in ['super_admin', 'admin', 'registrar']:
                    redirect_url = '/dashboard/admin/'
                elif user.user_type == 'finance':
                    redirect_url = '/dashboard/finance/'
                elif user.user_type in ['staff', 'lecturer']:
                    redirect_url = '/dashboard/staff/'
                elif user.user_type == 'hr':
                    redirect_url = '/dashboard/hr/'
                elif user.user_type == 'student':
                    redirect_url = '/dashboard/student/'
                
                print(f"Redirect URL: {redirect_url}")
                print("=" * 50)
                
                response = Response({
                    'success': True,
                    'session_key': request.session.session_key,
                    'redirect_url': redirect_url,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'user_type': user.user_type,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'is_superuser': user.is_superuser,
                        'is_authenticated': True,
                    }
                })
                
                response.set_cookie(
                    key='sessionid',
                    value=request.session.session_key,
                    secure=True,
                    httponly=True,
                    samesite='Lax',
                    max_age=1209600,
                    path='/'
                )
                
                return response
            
            print(f"Login failed: {serializer.errors}")
            return Response({'success': False, 'detail': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            print(f"ERROR during login: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'], url_path='logout')
    def logout(self, request):
        auth_logout(request)
        return Response({'success': True, 'message': 'Logged out successfully'})
    
@action(detail=False, methods=['get'], url_path='current_user')
def current_user(self, request):
    try:
        # Check if user is authenticated via session
        if request.user.is_authenticated:
            user = request.user
            return Response({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'user_type': user.user_type,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_superuser': user.is_superuser,
                'is_authenticated': True,
                'is_active': user.is_active,
            })
        
        return Response({'is_authenticated': False}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        print(f"Error in current_user: {e}")
        return Response({'is_authenticated': False, 'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
    
    @action(detail=False, methods=['post'], url_path='setup-admin')
    def setup_admin(self, request):
        """Create admin user if it doesn't exist"""
        try:
            User = get_user_model()
            if User.objects.filter(username='admin').exists():
                return Response({
                    'success': False,
                    'message': 'Admin user already exists',
                    'username': 'admin'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@glide-erp.com',
                password='admin123',
                user_type='super_admin',
                first_name='Admin',
                last_name='User'
            )
            
            return Response({
                'success': True,
                'message': 'Admin user created successfully!',
                'username': 'admin',
                'password': 'admin123'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], url_path='create-admin')
    def create_admin(self, request):
        """Endpoint to create admin user (for first-time setup)"""
        try:
            User = get_user_model()
            if User.objects.filter(username='admin').exists():
                return Response({
                    'success': False,
                    'message': 'Admin user already exists'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@glide-erp.com',
                password='admin123',
                user_type='super_admin',
                first_name='Admin',
                last_name='User'
            )
            
            return Response({
                'success': True,
                'message': 'Admin user created successfully!',
                'username': 'admin',
                'password': 'admin123'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create']:
            return [AllowAny()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return super().get_permissions()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    def get_queryset(self):
        queryset = User.objects.all()
        
        search = self.request.query_params.get('search', '')
        user_type = self.request.query_params.get('user_type', '')
        is_active = self.request.query_params.get('is_active', '')
        
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        if user_type:
            queryset = queryset.filter(user_type=user_type)
        if is_active != '':
            is_active_bool = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active_bool)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        print("=" * 50)
        print("CREATE USER CALLED")
        print(f"Request data: {request.data}")
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            password = getattr(user, '_created_password', None)
            response_data = serializer.data
            if password:
                response_data['password'] = password
            print(f"User created: {user.username} with password: {password}")
            print("=" * 50)
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            print(f"Serializer errors: {serializer.errors}")
            print("=" * 50)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def current_user(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


# ============================================
# DEPARTMENT VIEWSET
# ============================================
class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


# ============================================
# COURSE CATEGORY VIEWSET
# ============================================
class CourseCategoryViewSet(viewsets.ModelViewSet):
    queryset = CourseCategory.objects.all()
    serializer_class = CourseCategorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdmin()]
        return super().get_permissions()


# ============================================
# COURSE VIEWSET
# ============================================
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdmin()]
        return super().get_permissions()
    
    def get_queryset(self):
        queryset = Course.objects.all()
        
        search = self.request.query_params.get('search', '')
        category = self.request.query_params.get('category__category_type', '')
        duration = self.request.query_params.get('duration', '')
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search)
            )
        if category:
            queryset = queryset.filter(category__category_type=category)
        if duration:
            queryset = queryset.filter(duration=duration)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        category = request.query_params.get('category')
        courses = Course.objects.filter(category__category_type=category, is_active=True)
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)


# ============================================
# CLASS VIEWSET
# ============================================
class ClassViewSet(viewsets.ModelViewSet):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdmin()]
        return super().get_permissions()
    
    def get_queryset(self):
        queryset = Class.objects.all()
        
        search = self.request.query_params.get('search', '')
        course = self.request.query_params.get('course', '')
        is_active = self.request.query_params.get('is_active', '')
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search) |
                Q(academic_year__icontains=search)
            )
        if course and course.isdigit():
            queryset = queryset.filter(course_id=int(course))
        if is_active != '':
            is_active_bool = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active_bool)
        
        return queryset


# ============================================
# STUDENT VIEWSET
# ============================================
class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        queryset = Student.objects.all()
        
        search = self.request.query_params.get('search', '')
        status = self.request.query_params.get('status', '')
        course = self.request.query_params.get('course', '')
        
        print(f"🔍 Student filters - search: '{search}', status: '{status}', course: '{course}'")
        
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(registration_number__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search)
            )
        if status:
            queryset = queryset.filter(status=status)
        if course and course.isdigit():
            queryset = queryset.filter(course_id=int(course))
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def my_profile(self, request):
        try:
            student = Student.objects.get(user=request.user)
            serializer = StudentSerializer(student)
            return Response(serializer.data)
        except Student.DoesNotExist:
            return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def academic_progress(self, request, pk=None):
        student = self.get_object()
        return Response({'message': 'Academic progress data'})


# ============================================
# STUDENT APPLICATION VIEWSET
# ============================================
class StudentApplicationViewSet(viewsets.ModelViewSet):
    queryset = StudentApplication.objects.all()
    serializer_class = StudentApplicationSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_permissions(self):
        if self.action in ['create', 'submit_application']:
            return [AllowAny()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdmin()]
        return super().get_permissions()
    
    def get_queryset(self):
        queryset = StudentApplication.objects.all()
        
        search = self.request.query_params.get('search', '')
        status = self.request.query_params.get('status', '')
        category = self.request.query_params.get('category', '')
        
        print(f"🔍 Application filters - search: '{search}', status: '{status}', category: '{category}'")
        
        if search:
            queryset = queryset.filter(
                Q(application_id__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(full_name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search)
            )
        if status:
            queryset = queryset.filter(status=status)
        if category:
            queryset = queryset.filter(course_type=category)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        application = self.get_object()
        status_update = request.data.get('status')
        notes = request.data.get('notes', '')
        interview_date = request.data.get('interview_date')
        
        if status_update:
            application.status = status_update
            application.review_notes = notes
            application.reviewed_by = request.user
            application.decision_date = timezone.now().date()
            if interview_date:
                application.interview_date = interview_date
            application.save()
            serializer = self.get_serializer(application)
            return Response(serializer.data)
        return Response({'error': 'Status is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def submit_application(self, request):
        """Public endpoint for submitting applications"""
        try:
            data = request.data
            files = request.FILES
            
            application = StudentApplication.objects.create(
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
                full_name=data.get('full_name', ''),
                phone=data.get('phone', ''),
                email=data.get('email', ''),
                alternate_phone=data.get('alt_phone', ''),
                alternate_email=data.get('alt_email', ''),
                address=data.get('address', ''),
                permanent_address=data.get('permanent_address', ''),
                date_of_birth=data.get('dob') or None,
                marital_status=data.get('marital_status', ''),
                religion=data.get('religion', ''),
                citizenship=data.get('citizenship', ''),
                home_district=data.get('home_district', ''),
                home_parish=data.get('home_parish', ''),
                home_village=data.get('home_village', ''),
                course_type=data.get('course_type', ''),
                program_applied=data.get('program_applied', ''),
                program_level=data.get('occupational_level', ''),
                modular_course=data.get('modular_course', ''),
                diploma_course=data.get('diploma_course', ''),
                level_applied=data.get('level_applied', ''),
                academic_background=data.get('academic_background', ''),
                employment_experience=data.get('employment_experience', ''),
                uce_index=data.get('uce_index', ''),
                uce_year=data.get('uce_year', ''),
                uce_summary=data.get('uce_summary', ''),
                uce_subjects=self._get_subjects(data, 'uce'),
                uace_index=data.get('uace_index', ''),
                uace_year=data.get('uace_year', ''),
                uace_overall_grade=data.get('uace_overall_grade', ''),
                uace_subjects=self._get_subjects(data, 'uace'),
                other_qual_from=data.get('other_qual_from', ''),
                other_qual_to=data.get('other_qual_to', ''),
                other_qual_institution=data.get('other_qual_institution', ''),
                other_qual_qualification=data.get('other_qual_qualification', ''),
                other_qual_class=data.get('other_qual_class', ''),
                prev_reg_number=data.get('prev_reg_number', ''),
                prev_institution=data.get('prev_institution', ''),
                prev_program=data.get('prev_program', ''),
                job_position=data.get('job_position', ''),
                job_employer=data.get('job_employer', ''),
                job_period=data.get('job_period', ''),
                guardian_relationship=data.get('guardian_relationship', ''),
                guardian_name=data.get('guardian_name', ''),
                guardian_nationality=data.get('guardian_nationality', ''),
                guardian_phone=data.get('guardian_phone', ''),
                guardian_residence=data.get('guardian_residence', ''),
                referee1_name=data.get('referee1_name', ''),
                referee1_address=data.get('referee1_address', ''),
                referee1_phone=data.get('referee1_phone', ''),
                referee1_email=data.get('referee1_email', ''),
                referee2_name=data.get('referee2_name', ''),
                referee2_address=data.get('referee2_address', ''),
                referee2_phone=data.get('referee2_phone', ''),
                referee2_email=data.get('referee2_email', ''),
                declaration_signature=data.get('signature', ''),
                declaration_date=data.get('declaration_date') or None,
                declaration_agreed=data.get('declaration_check') == 'on',
                status='pending'
            )
            
            if 'payment_receipt' in files:
                application.payment_receipt = files['payment_receipt']
            if 'uce_certificate' in files:
                application.uce_certificate = files['uce_certificate']
            if 'uace_certificate' in files:
                application.uace_certificate = files['uace_certificate']
            if 'other_qual_certificate' in files:
                application.other_qual_certificate = files['other_qual_certificate']
            
            application.save()
            
            return Response({
                'success': True,
                'message': 'Application submitted successfully!',
                'application_id': application.application_id,
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(f"Application submission error: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def _get_subjects(self, data, prefix):
        subjects = {}
        for key, value in data.items():
            if key.startswith(f'{prefix}_subject_'):
                num = key.replace(f'{prefix}_subject_', '')
                grade_key = f'{prefix}_grade_{num}'
                subjects[value] = data.get(grade_key, '')
        return subjects


# ============================================
# INVOICE VIEWSET
# ============================================
class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated, IsFinance]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'generate_invoice', 'mark_paid']:
            return [IsAuthenticated(), IsFinance()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        queryset = Invoice.objects.all()
        
        search = self.request.query_params.get('search', '')
        student = self.request.query_params.get('student', '')
        status = self.request.query_params.get('status', '')
        issue_date_gte = self.request.query_params.get('issue_date__gte', '')
        issue_date_lte = self.request.query_params.get('issue_date__lte', '')
        
        if search:
            queryset = queryset.filter(
                Q(invoice_number__icontains=search) |
                Q(student__first_name__icontains=search) |
                Q(student__last_name__icontains=search) |
                Q(student__registration_number__icontains=search)
            )
        if student and student.isdigit():
            queryset = queryset.filter(student_id=int(student))
        if status:
            queryset = queryset.filter(status=status)
        if issue_date_gte:
            queryset = queryset.filter(issue_date__gte=issue_date_gte)
        if issue_date_lte:
            queryset = queryset.filter(issue_date__lte=issue_date_lte)
        
        return queryset
    
    @action(detail=False, methods=['post'], url_path='generate_invoice')
    def generate_invoice(self, request):
        student_id = request.data.get('student_id')
        semester_id = request.data.get('semester_id')
        
        if not student_id or not semester_id:
            return Response({
                'success': False,
                'error': 'Student ID and Semester ID are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            student = Student.objects.get(id=student_id)
            semester = Semester.objects.get(id=semester_id)
            
            fee_structures = FeeStructure.objects.filter(
                course=student.course,
                academic_year=semester.academic_year.name,
                is_active=True
            )
            
            if not fee_structures.exists():
                return Response({
                    'success': False,
                    'error': 'No fee structures found for this course'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            total_amount = fee_structures.aggregate(total=Sum('amount'))['total'] or 0
            
            existing_invoice = Invoice.objects.filter(
                student=student,
                semester=semester
            ).first()
            
            if existing_invoice:
                return Response({
                    'success': False,
                    'error': 'Invoice already exists for this student and semester',
                    'invoice_number': existing_invoice.invoice_number
                }, status=status.HTTP_400_BAD_REQUEST)
            
            invoice = Invoice.objects.create(
                student=student,
                semester=semester,
                due_date=timezone.now().date() + timedelta(days=30),
                total_amount=total_amount,
                status='issued'
            )
            
            serializer = InvoiceSerializer(invoice)
            return Response({
                'success': True,
                'message': 'Invoice generated successfully',
                'invoice': serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
        except Semester.DoesNotExist:
            return Response({'error': 'Semester not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error generating invoice: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        invoice = self.get_object()
        amount = request.data.get('amount', 0)
        payment_method = request.data.get('payment_method', 'cash')
        
        try:
            payment = Payment.objects.create(
                invoice=invoice,
                student=invoice.student,
                amount=amount,
                payment_method=payment_method,
                recorded_by=request.user
            )
            invoice.amount_paid += amount
            invoice.balance = invoice.total_amount - invoice.amount_paid
            if invoice.balance <= 0:
                invoice.status = 'fully_paid'
            else:
                invoice.status = 'partially_paid'
            invoice.save()
            
            return Response({
                'success': True,
                'message': 'Payment recorded successfully',
                'payment': PaymentSerializer(payment).data
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ============================================
# HTML LOGIN/LOGOUT VIEWS (For Browser Form Submissions)
# ============================================
@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            
            if user.user_type in ['super_admin', 'admin', 'registrar']:
                return redirect('/dashboard/admin/')
            elif user.user_type == 'finance':
                return redirect('/dashboard/finance/')
            elif user.user_type in ['staff', 'lecturer']:
                return redirect('/dashboard/staff/')
            elif user.user_type == 'hr':
                return redirect('/dashboard/hr/')
            else:
                return redirect('/dashboard/student/')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'login.html')


def logout_view(request):
    auth_logout(request)
    return redirect('/login/')
