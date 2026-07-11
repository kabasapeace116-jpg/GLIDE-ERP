from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta

from .models import FeeStructure, Invoice, Payment, FinancialClearance
from .serializers import (
    FeeStructureSerializer, InvoiceSerializer, 
    PaymentSerializer, FinancialClearanceSerializer
)

# Import models from core
from core.models import Student, User
from core.permissions import IsAdmin, IsStaff, IsFinance
from admissions.models import Semester


class FeeStructureViewSet(viewsets.ModelViewSet):
    queryset = FeeStructure.objects.all()
    serializer_class = FeeStructureSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        # Allow finance and admin to manage fee structures
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsFinance()]
        # Allow viewing for finance and admin
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """Override to add filtering and search"""
        queryset = FeeStructure.objects.all()
        
        # Get filter parameters
        search = self.request.query_params.get('search', '')
        course = self.request.query_params.get('course', '')
        fee_type = self.request.query_params.get('fee_type', '')
        
        print(f"FeeStructure search: search='{search}', course='{course}', fee_type='{fee_type}'")
        
        try:
            # Apply search filter
            if search:
                queryset = queryset.filter(
                    Q(course__name__icontains=search) |
                    Q(fee_type__icontains=search) |
                    Q(academic_year__icontains=search)
                )
            
            # Apply course filter
            if course and course.isdigit():
                queryset = queryset.filter(course_id=int(course))
            
            # Apply fee type filter
            if fee_type:
                queryset = queryset.filter(fee_type=fee_type)
            
            return queryset
        except Exception as e:
            print(f"Error in FeeStructure get_queryset: {e}")
            # Return original queryset if there's an error
            return FeeStructure.objects.all()

    def list(self, request, *args, **kwargs):
        # Allow finance and admin to view
        if request.user.user_type not in ['admin', 'super_admin', 'finance']:
            return Response({
                'error': 'Permission denied. Only finance and admin users can access fee structures.'
            }, status=status.HTTP_403_FORBIDDEN)
        return super().list(request, *args, **kwargs)


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated, IsFinance]

    def get_queryset(self):
        """Override to add filtering and search"""
        queryset = Invoice.objects.all()
        
        # Get filter parameters
        search = self.request.query_params.get('search', '')
        student = self.request.query_params.get('student', '')
        status = self.request.query_params.get('status', '')
        issue_date_gte = self.request.query_params.get('issue_date__gte', '')
        issue_date_lte = self.request.query_params.get('issue_date__lte', '')
        
        try:
            # Apply search filter
            if search:
                queryset = queryset.filter(
                    Q(invoice_number__icontains=search) |
                    Q(student__first_name__icontains=search) |
                    Q(student__last_name__icontains=search) |
                    Q(student__registration_number__icontains=search)
                )
            
            # Apply student filter
            if student and student.isdigit():
                queryset = queryset.filter(student_id=int(student))
            
            # Apply status filter
            if status:
                queryset = queryset.filter(status=status)
            
            # Apply date filters
            if issue_date_gte:
                queryset = queryset.filter(issue_date__gte=issue_date_gte)
            if issue_date_lte:
                queryset = queryset.filter(issue_date__lte=issue_date_lte)
            
            return queryset
        except Exception as e:
            print(f"Error in Invoice get_queryset: {e}")
            return Invoice.objects.all()

    
    @action(detail=False, methods=['post'])
    def generate_invoice(self, request):
        student_id = request.data.get('student_id')
        semester_id = request.data.get('semester_id')
        try:
            student = Student.objects.get(id=student_id)
            semester = Semester.objects.get(id=semester_id)
            
            # Get fee structure for the student's course
            fee_structures = FeeStructure.objects.filter(
                course=student.course,
                academic_year=semester.academic_year.name,
                is_active=True
            )
            total_amount = fee_structures.aggregate(total=Sum('amount'))['total'] or 0
            
            # Check if invoice already exists
            existing = Invoice.objects.filter(student=student, semester=semester).first()
            if existing:
                return Response({
                    'error': 'Invoice already exists',
                    'invoice_number': existing.invoice_number
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


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, IsFinance]
    
    def get_queryset(self):
        """Override to add filtering and search"""
        queryset = Payment.objects.all()
        
        # Get filter parameters
        search = self.request.query_params.get('search', '')
        payment_method = self.request.query_params.get('payment_method', '')
        payment_date_gte = self.request.query_params.get('payment_date__gte', '')
        payment_date_lte = self.request.query_params.get('payment_date__lte', '')
        student = self.request.query_params.get('student', '')
        
        try:
            # Apply search filter
            if search:
                queryset = queryset.filter(
                    Q(payment_number__icontains=search) |
                    Q(student__first_name__icontains=search) |
                    Q(student__last_name__icontains=search) |
                    Q(student__registration_number__icontains=search)
                )
            
            # Apply payment method filter
            if payment_method:
                queryset = queryset.filter(payment_method=payment_method)
            
            # Apply date filters
            if payment_date_gte:
                queryset = queryset.filter(payment_date__gte=payment_date_gte)
            if payment_date_lte:
                queryset = queryset.filter(payment_date__lte=payment_date_lte)
            
            # Apply student filter
            if student and student.isdigit():
                queryset = queryset.filter(student_id=int(student))
            
            return queryset
        except Exception as e:
            print(f"Error in Payment get_queryset: {e}")
            return Payment.objects.all()
        
    @action(detail=False, methods=['get'])
    def student_payments(self, request):
        student_id = request.query_params.get('student_id')
        payments = Payment.objects.filter(student_id=student_id)
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)
    def get_queryset(self):
        """Override to add filtering and search"""
        queryset = super().get_queryset()
        
        # Get filter parameters
        search = self.request.query_params.get('search', '')
        payment_method = self.request.query_params.get('payment_method', '')
        payment_date_gte = self.request.query_params.get('payment_date__gte', '')
        payment_date_lte = self.request.query_params.get('payment_date__lte', '')
        student = self.request.query_params.get('student', '')
        invoice = self.request.query_params.get('invoice', '')
        
        # Apply search filter
        if search:
            queryset = queryset.filter(
                Q(payment_number__icontains=search) |
                Q(student__first_name__icontains=search) |
                Q(student__last_name__icontains=search) |
                Q(student__registration_number__icontains=search)
            )
        
        # Apply payment method filter
        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)
        
        # Apply date filters
        if payment_date_gte:
            queryset = queryset.filter(payment_date__gte=payment_date_gte)
        if payment_date_lte:
            queryset = queryset.filter(payment_date__lte=payment_date_lte)
        
        # Apply student filter
        if student:
            queryset = queryset.filter(student_id=student)
        
        # Apply invoice filter
        if invoice:
            queryset = queryset.filter(invoice_id=invoice)
        
        return queryset


class FinancialClearanceViewSet(viewsets.ModelViewSet):
    queryset = FinancialClearance.objects.all()
    serializer_class = FinancialClearanceSerializer
    permission_classes = [IsAuthenticated, IsFinance]
    
    @action(detail=False, methods=['post'])
    def clear_student(self, request):
        student_id = request.data.get('student_id')
        semester_id = request.data.get('semester_id')
        try:
            student = Student.objects.get(id=student_id)
            semester = Semester.objects.get(id=semester_id)
            
            clearance, created = FinancialClearance.objects.get_or_create(
                student=student,
                semester=semester,
                defaults={
                    'is_cleared': True,
                    'cleared_by': request.user,
                    'clearance_date': timezone.now().date()
                }
            )
            if not created:
                clearance.is_cleared = True
                clearance.clearance_date = timezone.now().date()
                clearance.cleared_by = request.user
                clearance.save()
                
            return Response({
                'success': True,
                'message': 'Student cleared successfully',
                'clearance': FinancialClearanceSerializer(clearance).data
            })
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
        except Semester.DoesNotExist:
            return Response({'error': 'Semester not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def reverse_clearance(self, request, pk=None):
        clearance = self.get_object()
        clearance.is_cleared = False
        clearance.clearance_date = None
        clearance.save()
        return Response({
            'success': True,
            'message': 'Clearance reversed successfully'
        })
    def get_queryset(self):
        """Override to add filtering and search"""
        queryset = super().get_queryset()
        
        # Get filter parameters
        search = self.request.query_params.get('search', '')
        is_cleared = self.request.query_params.get('is_cleared', '')
        semester = self.request.query_params.get('semester', '')
        
        # Apply search filter
        if search:
            queryset = queryset.filter(
                Q(student__first_name__icontains=search) |
                Q(student__last_name__icontains=search) |
                Q(student__registration_number__icontains=search)
            )
        
        # Apply clearance status filter
        if is_cleared != '':
            # Convert string to boolean
            is_cleared_bool = is_cleared.lower() == 'true'
            queryset = queryset.filter(is_cleared=is_cleared_bool)
        
        # Apply semester filter
        if semester:
            queryset = queryset.filter(semester_id=semester)
        
        return queryset

    @action(detail=False, methods=['post'])
    def bulk_clear(self, request):
        semester_id = request.data.get('semester_id')
        if not semester_id:
            return Response({'error': 'Semester ID required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            semester = Semester.objects.get(id=semester_id)
            pending = FinancialClearance.objects.filter(semester=semester, is_cleared=False)
            count = 0
            
            for clearance in pending:
                clearance.is_cleared = True
                clearance.clearance_date = timezone.now().date()
                clearance.cleared_by = request.user
                clearance.save()
                count += 1
            
            return Response({
                'success': True,
                'message': f'{count} students cleared successfully',
                'cleared_count': count
            })
        except Semester.DoesNotExist:
            return Response({'error': 'Semester not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)