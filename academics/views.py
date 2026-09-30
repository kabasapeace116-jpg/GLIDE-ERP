from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, Count, Q
from django.utils import timezone
from .models import CourseUnit, Timetable, Assessment, Result, StudentCourseProgress, AttendanceRecord
from .serializers import (
    CourseUnitSerializer, TimetableSerializer, AssessmentSerializer,
    ResultSerializer, StudentCourseProgressSerializer, AttendanceRecordSerializer
)
from core.permissions import IsAdmin, IsStaff, IsStudent, IsLecturer

class CourseUnitViewSet(viewsets.ModelViewSet):
    queryset = CourseUnit.objects.all()
    serializer_class = CourseUnitSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdmin()]
        return super().get_permissions()
    
    def get_queryset(self):
        """Override to add filtering and search"""
        queryset = CourseUnit.objects.all()
        search = self.request.query_params.get('search', '')
        
        try:
            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search) |
                    Q(code__icontains=search) |
                    Q(course__name__icontains=search)
                )
            return queryset
        except Exception as e:
            print(f"Error in CourseUnit get_queryset: {e}")
            return CourseUnit.objects.all()


class AssessmentViewSet(viewsets.ModelViewSet):
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
    permission_classes = [IsAuthenticated, IsStaff]
    
    def get_queryset(self):
        """Override to add filtering and search"""
        queryset = Assessment.objects.all()
        
        search = self.request.query_params.get('search', '')
        assessment_type = self.request.query_params.get('assessment_type', '')
        is_published = self.request.query_params.get('is_published', '')
        
        try:
            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search) |
                    Q(course_unit__name__icontains=search) |
                    Q(course_unit__code__icontains=search)
                )
            
            if assessment_type:
                queryset = queryset.filter(assessment_type=assessment_type)
            
            if is_published != '':
                is_published_bool = is_published.lower() == 'true'
                queryset = queryset.filter(is_published=is_published_bool)
            
            return queryset
        except Exception as e:
            print(f"Error in Assessment get_queryset: {e}")
            return Assessment.objects.all()
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        assessment = self.get_object()
        assessment.is_published = True
        assessment.save()
        return Response({'message': 'Assessment published successfully'})
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        assessment = self.get_object()
        assessment.is_closed = True
        assessment.save()
        return Response({'message': 'Assessment closed successfully'})


class ResultViewSet(viewsets.ModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = [IsAuthenticated, IsStaff]
    
    def get_queryset(self):
        """Override to add filtering and search"""
        queryset = Result.objects.all()
        
        search = self.request.query_params.get('search', '')
        course = self.request.query_params.get('course', '')
        is_published = self.request.query_params.get('is_published', '')
        student_id = self.request.query_params.get('student_id', '')
        semester_id = self.request.query_params.get('semester_id', '')
        
        try:
            if search:
                queryset = queryset.filter(
                    Q(student__first_name__icontains=search) |
                    Q(student__last_name__icontains=search) |
                    Q(student__registration_number__icontains=search) |
                    Q(course_unit__name__icontains=search) |
                    Q(course_unit__code__icontains=search)
                )
            
            if course and course.isdigit():
                queryset = queryset.filter(course_unit__course_id=int(course))
            
            if is_published != '':
                is_published_bool = is_published.lower() == 'true'
                queryset = queryset.filter(is_published=is_published_bool)
            
            if student_id and student_id.isdigit():
                queryset = queryset.filter(student_id=int(student_id))
            
            if semester_id and semester_id.isdigit():
                queryset = queryset.filter(semester_id=int(semester_id))
            
            return queryset
        except Exception as e:
            print(f"Error in Result get_queryset: {e}")
            return Result.objects.all()
    
    @action(detail=False, methods=['post'])
    def bulk_upload(self, request):
        results_data = request.data.get('results', [])
        for data in results_data:
            serializer = ResultSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
        return Response({'message': f'{len(results_data)} results uploaded'})
    
    @action(detail=False, methods=['get'])
    def student_results(self, request):
        student_id = request.query_params.get('student_id')
        semester_id = request.query_params.get('semester_id')
        results = Result.objects.filter(student_id=student_id)
        if semester_id:
            results = results.filter(semester_id=semester_id)
        serializer = ResultSerializer(results, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        result = self.get_object()
        result.is_published = True
        result.published_date = timezone.now().date()
        result.save()
        return Response({'message': 'Result published successfully'})


class AttendanceRecordViewSet(viewsets.ModelViewSet):
    queryset = AttendanceRecord.objects.all()
    serializer_class = AttendanceRecordSerializer
    permission_classes = [IsAuthenticated, IsStaff]
    
    def get_queryset(self):
        """Override to add filtering and search"""
        queryset = AttendanceRecord.objects.all()
        
        search = self.request.query_params.get('search', '')
        date = self.request.query_params.get('date', '')
        status_filter = self.request.query_params.get('status', '')
        student_id = self.request.query_params.get('student_id', '')
        
        try:
            if search:
                queryset = queryset.filter(
                    Q(student__first_name__icontains=search) |
                    Q(student__last_name__icontains=search) |
                    Q(student__registration_number__icontains=search)
                )
            
            if date:
                queryset = queryset.filter(date=date)
            
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            
            if student_id and student_id.isdigit():
                queryset = queryset.filter(student_id=int(student_id))
            
            return queryset
        except Exception as e:
            print(f"Error in AttendanceRecord get_queryset: {e}")
            return AttendanceRecord.objects.all()
    
    @action(detail=False, methods=['post'])
    def record_attendance(self, request):
        data = request.data
        attendance = AttendanceRecord.objects.create(
            student_id=data.get('student_id'),
            class_obj_id=data.get('class_obj'),
            course_unit_id=data.get('course_unit'),
            date=data.get('date'),
            status=data.get('status'),
            time_in=data.get('time_in'),
            time_out=data.get('time_out'),
            recorded_by=request.user
        )
        serializer = AttendanceRecordSerializer(attendance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def student_attendance(self, request):
        student_id = request.query_params.get('student_id')
        attendance = AttendanceRecord.objects.filter(student_id=student_id)
        total = attendance.count()
        present = attendance.filter(status='present').count()
        absent = attendance.filter(status='absent').count()
        late = attendance.filter(status='late').count()
        
        return Response({
            'total': total,
            'present': present,
            'absent': absent,
            'late': late,
            'attendance_rate': f"{(present/total*100):.1f}%" if total > 0 else "0%"
        })


class TimetableViewSet(viewsets.ModelViewSet):
    queryset = Timetable.objects.all()
    serializer_class = TimetableSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Override to add filtering"""
        queryset = Timetable.objects.all()
        
        class_id = self.request.query_params.get('class', '')
        semester_id = self.request.query_params.get('semester', '')
        
        try:
            if class_id and class_id.isdigit():
                queryset = queryset.filter(class_obj_id=int(class_id))
            
            if semester_id and semester_id.isdigit():
                queryset = queryset.filter(semester_id=int(semester_id))
            
            return queryset
        except Exception as e:
            print(f"Error in Timetable get_queryset: {e}")
            return Timetable.objects.all()

from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from .models import Certificate
from .serializers import CertificateSerializer
from .services.certificate_service import (
    issue_certificate, generate_certificate_pdf, check_certificate_eligibility
)


class CertificateViewSet(viewsets.ModelViewSet):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    permission_classes = [IsAuthenticated, IsStaff]

    def get_queryset(self):
        queryset = Certificate.objects.all()
        search = self.request.query_params.get('search', '')
        student_id = self.request.query_params.get('student_id', '')
        cert_type = self.request.query_params.get('certificate_type', '')
        status_filter = self.request.query_params.get('status', '')

        try:
            if search:
                queryset = queryset.filter(
                    Q(certificate_number__icontains=search) |
                    Q(student__first_name__icontains=search) |
                    Q(student__last_name__icontains=search) |
                    Q(student__registration_number__icontains=search)
                )
            if student_id and student_id.isdigit():
                queryset = queryset.filter(student_id=int(student_id))
            if cert_type:
                queryset = queryset.filter(certificate_type=cert_type)
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            return queryset
        except Exception as e:
            print(f"Error in Certificate get_queryset: {e}")
            return Certificate.objects.all()

    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        POST body:
        {
          "student_id": 12,
          "certificate_type": "program_completion",
          "course_unit_id": null,        # required for course_completion
          "semester_id": null,
          "academic_year_id": null,
          "description": "optional"
        }
        """
        from core.models import Student
        from admissions.models import Semester, AcademicYear

        student_id = request.data.get('student_id')
        cert_type = request.data.get('certificate_type')

        if not student_id or not cert_type:
            return Response(
                {'error': 'student_id and certificate_type are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        student = get_object_or_404(Student, pk=student_id)

        course_unit = None
        course_unit_id = request.data.get('course_unit_id')
        if course_unit_id:
            course_unit = get_object_or_404(CourseUnit, pk=course_unit_id)

        semester = None
        if request.data.get('semester_id'):
            semester = get_object_or_404(Semester, pk=request.data['semester_id'])

        academic_year = None
        if request.data.get('academic_year_id'):
            academic_year = get_object_or_404(
                AcademicYear, pk=request.data['academic_year_id']
            )

        try:
            certificate = issue_certificate(
                student=student,
                certificate_type=cert_type,
                issued_by=request.user,
                course_unit=course_unit,
                semester=semester,
                academic_year=academic_year,
                description=request.data.get('description', ''),
            )
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            CertificateSerializer(certificate).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=['get'])
    def eligibility(self, request):
        """GET ?student_id=12&certificate_type=program_completion[&course_unit_id=3]"""
        from core.models import Student

        student_id = request.query_params.get('student_id')
        cert_type = request.query_params.get('certificate_type')
        course_unit_id = request.query_params.get('course_unit_id')

        if not student_id or not cert_type:
            return Response(
                {'error': 'student_id and certificate_type are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        student = get_object_or_404(Student, pk=student_id)
        course_unit = None
        if course_unit_id:
            course_unit = get_object_or_404(CourseUnit, pk=course_unit_id)

        eligible, reason = check_certificate_eligibility(
            student, cert_type, course_unit
        )
        return Response({'eligible': eligible, 'reason': reason})

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        certificate = self.get_object()
        pdf = generate_certificate_pdf(certificate)
        filename = f"{certificate.certificate_number}.pdf"
        return FileResponse(
            pdf, as_attachment=True, filename=filename, content_type='application/pdf'
        )

    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        certificate = self.get_object()
        certificate.status = 'revoked'
        certificate.save()
        return Response({'message': 'Certificate revoked.'})


class VerifyCertificateView(APIView):
    """
    Public endpoint: GET /api/academics/certificates/verify/<verification_code>/
    Lets anyone confirm a certificate is genuine.
    """
    permission_classes = [AllowAny]

    def get(self, request, verification_code):
        try:
            cert = Certificate.objects.get(
                verification_code=verification_code, status='issued'
            )
        except Certificate.DoesNotExist:
            return Response(
                {'valid': False, 'message': 'Certificate not found or not active.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response({
            'valid': True,
            'certificate_number': cert.certificate_number,
            'student_name': cert.snapshot_data.get('student', {}).get('full_name'),
            'certificate_type': cert.get_certificate_type_display(),
            'issue_date': cert.issue_date,
        })