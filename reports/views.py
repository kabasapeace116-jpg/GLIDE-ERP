from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum, Avg, Q, F, Value
from django.db.models.functions import Coalesce
from django.utils import timezone
from core.models import Student, Course, Class
from academics.models import Result, AttendanceRecord, Assessment
from finance.models import Invoice, Payment, FinancialClearance
from core.permissions import IsAdmin, IsStaff, IsFinance


class ReportViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def student_statistics(self, request):
        if request.user.user_type not in ['admin', 'super_admin', 'staff', 'finance']:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        total_students = Student.objects.count()
        active_students = Student.objects.filter(status='active').count()
        graduated_students = Student.objects.filter(status='graduated').count()
        by_course = Course.objects.annotate(
            student_count=Count('students')
        ).values('name', 'student_count')
        by_status = Student.objects.values('status').annotate(count=Count('id'))
        
        return Response({
            'total_students': total_students,
            'active_students': active_students,
            'graduated_students': graduated_students,
            'by_course': by_course,
            'by_status': by_status
        })
    
    @action(detail=False, methods=['get'])
    def academic_performance(self, request):
        if request.user.user_type not in ['admin', 'super_admin', 'staff', 'finance']:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        results = Result.objects.filter(is_published=True)
        total_results = results.count()
        avg_score = results.aggregate(Avg('score'))['score__avg'] or 0
        
        grade_distribution = results.values('grade').annotate(count=Count('id'))
        
        by_course = results.values('course_unit__course__name').annotate(
            avg_score=Avg('score'),
            student_count=Count('student', distinct=True)
        )
        
        return Response({
            'total_results': total_results,
            'average_score': avg_score,
            'grade_distribution': grade_distribution,
            'by_course': by_course
        })
    
    @action(detail=False, methods=['get'])
    def financial_summary(self, request):
        """Financial summary - accessible by finance and admin"""
        if request.user.user_type not in ['admin', 'super_admin', 'finance']:
            return Response({
                'error': 'Permission denied. Only finance and admin users can access financial reports.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            # Debug: Log counts
            print(f"Invoice count: {Invoice.objects.count()}")
            print(f"Payment count: {Payment.objects.count()}")
            
            # Get total invoices
            total_invoices_agg = Invoice.objects.aggregate(total=Sum('total_amount'))
            total_invoices = total_invoices_agg['total'] or 0
            
            # Get total payments
            total_payments_agg = Payment.objects.aggregate(total=Sum('amount'))
            total_payments = total_payments_agg['total'] or 0
            
            outstanding_balance = total_invoices - total_payments
            
            print(f"Total Invoices: {total_invoices}, Total Payments: {total_payments}, Outstanding: {outstanding_balance}")
            
            # Payments by method
            payments_by_method = Payment.objects.values('payment_method').annotate(
                total=Sum('amount'),
                count=Count('id')
            )
            
            # Convert to list of dicts with proper values
            payments_by_method_list = []
            for item in payments_by_method:
                payments_by_method_list.append({
                    'payment_method': item['payment_method'],
                    'total': float(item['total'] or 0),
                    'count': item['count']
                })
            
            # Get students with outstanding balances
            students_with_balance = []
            
            # Get invoices with balance > 0
            invoices_with_balance = Invoice.objects.filter(balance__gt=0).select_related('student', 'student__course')
            
            print(f"Invoices with balance: {invoices_with_balance.count()}")
            
            for invoice in invoices_with_balance[:20]:
                student_name = invoice.student.full_name if invoice.student else 'N/A'
                reg_number = invoice.student.registration_number if invoice.student else 'N/A'
                course_name = invoice.student.course.name if invoice.student and invoice.student.course else 'N/A'
                
                students_with_balance.append({
                    'student_name': student_name,
                    'registration_number': reg_number,
                    'course': course_name,
                    'balance': float(invoice.balance),
                    'invoice_number': invoice.invoice_number
                })
            
            # If no invoices with balance, check financial clearances
            if not students_with_balance:
                not_cleared = FinancialClearance.objects.filter(is_cleared=False).select_related('student', 'student__course')
                
                for clearance in not_cleared[:20]:
                    student_invoices = Invoice.objects.filter(student=clearance.student)
                    total_balance = student_invoices.aggregate(total=Sum('balance'))['total'] or 0
                    
                    if total_balance > 0:
                        student_name = clearance.student.full_name if clearance.student else 'N/A'
                        reg_number = clearance.student.registration_number if clearance.student else 'N/A'
                        course_name = clearance.student.course.name if clearance.student and clearance.student.course else 'N/A'
                        
                        students_with_balance.append({
                            'student_name': student_name,
                            'registration_number': reg_number,
                            'course': course_name,
                            'balance': float(total_balance)
                        })
            
            students_with_balance_count = len(students_with_balance)
            
            print(f"Students with balance: {students_with_balance_count}")
            
            return Response({
                'total_invoices': float(total_invoices),
                'total_payments': float(total_payments),
                'outstanding_balance': float(outstanding_balance),
                'payments_by_method': payments_by_method_list,
                'students_with_balance': students_with_balance_count,
                'students_with_balance_list': students_with_balance
            })
            
        except Exception as e:
            print(f"Error in financial_summary: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({
                'error': str(e),
                'total_invoices': 0,
                'total_payments': 0,
                'outstanding_balance': 0,
                'payments_by_method': [],
                'students_with_balance': 0,
                'students_with_balance_list': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def attendance_summary(self, request):
        if request.user.user_type not in ['admin', 'super_admin', 'staff', 'finance']:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        attendance_records = AttendanceRecord.objects.all()
        total = attendance_records.count()
        present = attendance_records.filter(status='present').count()
        absent = attendance_records.filter(status='absent').count()
        late = attendance_records.filter(status='late').count()
        excused = attendance_records.filter(status='excused').count()
        
        by_course = attendance_records.values('course_unit__course__name').annotate(
            total=Count('id'),
            present=Count('id', filter=Q(status='present')),
            absent=Count('id', filter=Q(status='absent')),
            late=Count('id', filter=Q(status='late'))
        )
        
        return Response({
            'total_records': total,
            'present': present,
            'absent': absent,
            'late': late,
            'excused': excused,
            'attendance_rate': f"{(present/total*100):.1f}%" if total > 0 else "0%",
            'by_course': by_course
        })
    
    @action(detail=False, methods=['get'])
    def course_enrollment(self, request):
        if request.user.user_type not in ['admin', 'super_admin', 'staff', 'finance']:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        course_data = Course.objects.annotate(
            student_count=Count('students'),
            class_count=Count('classes')
        ).values('name', 'code', 'student_count', 'class_count')
        
        return Response(course_data)
    
    @action(detail=False, methods=['get'])
    def generate_pdf(self, request):
        return Response({'message': 'PDF generation endpoint - Use reportlab to generate PDF reports'})