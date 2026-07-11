from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Employee, LeaveRequest, Attendance
from .serializers import EmployeeSerializer, LeaveRequestSerializer, AttendanceSerializer
from core.permissions import IsAdmin, IsStaff

# Get the User model
User = get_user_model()


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get_queryset(self):
        """Override to add filtering and search"""
        queryset = Employee.objects.all()
        
        # Get filter parameters
        search = self.request.query_params.get('search', '')
        status = self.request.query_params.get('status', '')
        department = self.request.query_params.get('department', '')
        
        print(f"🔍 Employee filters - search: '{search}', status: '{status}', department: '{department}'")
        
        try:
            # Apply search filter
            if search:
                queryset = queryset.filter(
                    Q(employee_number__icontains=search) |
                    Q(user__first_name__icontains=search) |
                    Q(user__last_name__icontains=search) |
                    Q(user__username__icontains=search) |
                    Q(position__icontains=search)
                )
            
            # Apply status filter
            if status:
                queryset = queryset.filter(status=status)
            
            # Apply department filter
            if department and department.isdigit():
                queryset = queryset.filter(department_id=int(department))
            
            # Apply ordering
            ordering = self.request.query_params.get('ordering', '-created_at')
            queryset = queryset.order_by(ordering)
            
            return queryset
        except Exception as e:
            print(f"Error in Employee get_queryset: {e}")
            return Employee.objects.all()
        
    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to ensure user data is included"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], url_path='create_with_user')
    def create_with_user(self, request):
        """Create a new user and employee together"""
        print("=" * 50)
        print("CREATE USER AND EMPLOYEE")
        print(f"Request data: {request.data}")
        
        try:
            data = request.data
            
            # Validate required fields
            required_fields = ['first_name', 'last_name', 'email', 'phone', 'position', 'department', 'employment_date', 'user_type']
            missing_fields = [f for f in required_fields if not data.get(f)]
            if missing_fields:
                return Response({
                    'error': f'Missing required fields: {", ".join(missing_fields)}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if user already exists by email
            if User.objects.filter(email=data['email']).exists():
                return Response({
                    'error': f'User with email {data["email"]} already exists'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Generate username if not provided
            username = data.get('username')
            if not username:
                username = f"{data['first_name'].lower()}.{data['last_name'].lower()}"
            
            # Check if username exists
            if User.objects.filter(username=username).exists():
                username = f"{username}{User.objects.filter(username__startswith=username).count() + 1}"
                print(f"Username taken, using: {username}")
            
            # Generate password if not provided
            password = data.get('password')
            if not password:
                import random
                import string
                # Generate a random password
                chars = string.ascii_letters + string.digits
                password = 'GLIDE' + ''.join(random.choices(chars, k=8))
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=data['email'],
                password=password,
                first_name=data['first_name'],
                last_name=data['last_name'],
                user_type=data['user_type'],
                phone=data.get('phone', ''),
                is_staff=True
            )
            print(f"✅ User created: {user.username}")
            
            # Generate employee number
            year = timezone.now().year
            last_emp = Employee.objects.filter(
                employee_number__startswith=f"EMP/{year}"
            ).order_by('-employee_number').first()
            seq = int(last_emp.employee_number.split('/')[-1]) + 1 if last_emp else 1
            emp_number = f"EMP/{year}/{seq:04d}"
            
            # Create employee
            employee = Employee.objects.create(
                user=user,
                employee_number=emp_number,
                position=data['position'],
                department_id=data['department'] if data['department'] else None,
                employment_type=data.get('employment_type', 'full_time'),
                status=data.get('status', 'active'),
                employment_date=data['employment_date'],
                contract_end_date=data.get('contract_end_date'),
                salary=data.get('salary', 0),
                nssf_number=data.get('nssf_number', ''),
                bank_name=data.get('bank_name', ''),
                bank_account=data.get('bank_account', ''),
                emergency_contact=data.get('emergency_contact', ''),
                emergency_phone=data.get('emergency_phone', '')
            )
            print(f"✅ Employee created: {employee.employee_number}")
            
            return Response({
                'id': employee.id,
                'employee_number': employee.employee_number,
                'username': user.username,
                'password': password,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'position': employee.position,
                'status': employee.status
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['put'], url_path='update_with_user')
    def update_with_user(self, request, pk=None):
        """Update both user and employee together"""
        print("=" * 50)
        print("UPDATE USER AND EMPLOYEE")
        print(f"Employee ID: {pk}")
        print(f"Request data: {request.data}")
        
        try:
            employee = self.get_object()
            user = employee.user
            data = request.data
            
            # Validate required fields
            required_fields = ['first_name', 'last_name', 'email', 'phone', 'position', 'department', 'employment_date', 'user_type']
            missing_fields = [f for f in required_fields if not data.get(f)]
            if missing_fields:
                return Response({
                    'error': f'Missing required fields: {", ".join(missing_fields)}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if email is taken by another user
            if User.objects.filter(email=data['email']).exclude(id=user.id).exists():
                return Response({
                    'error': f'Email {data["email"]} is already in use by another user'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Update user
            user.first_name = data['first_name']
            user.last_name = data['last_name']
            user.email = data['email']
            user.phone = data.get('phone', '')
            user.user_type = data['user_type']
            user.is_staff = True
            user.save()
            print(f"✅ User updated: {user.username}")
            
            # Update employee
            employee.position = data['position']
            employee.department_id = data['department'] if data['department'] else None
            employee.employment_type = data.get('employment_type', 'full_time')
            employee.status = data.get('status', 'active')
            employee.employment_date = data['employment_date']
            employee.contract_end_date = data.get('contract_end_date')
            employee.salary = data.get('salary', 0)
            employee.nssf_number = data.get('nssf_number', '')
            employee.bank_name = data.get('bank_name', '')
            employee.bank_account = data.get('bank_account', '')
            employee.emergency_contact = data.get('emergency_contact', '')
            employee.emergency_phone = data.get('emergency_phone', '')
            employee.save()
            print(f"✅ Employee updated: {employee.employee_number}")
            
            return Response({
                'id': employee.id,
                'employee_number': employee.employee_number,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'position': employee.position,
                'status': employee.status
            })
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated, IsStaff]
    
    def perform_create(self, serializer):
        serializer.save()
    
    def perform_update(self, serializer):
        if 'status' in serializer.validated_data:
            if serializer.validated_data['status'] == 'approved':
                serializer.validated_data['approval_date'] = timezone.now().date()
        serializer.save()


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated, IsStaff]