from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import AdmissionBatch, AdmittedStudent, AcademicYear, Semester
from .serializers import (
    AdmissionBatchSerializer, AdmittedStudentSerializer,
    AcademicYearSerializer, SemesterSerializer
)
from core.permissions import IsAdmin, IsStaff

class AcademicYearViewSet(viewsets.ModelViewSet):
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    
    @action(detail=False, methods=['post'])
    def set_current(self, request):
        year_id = request.data.get('year_id')
        try:
            year = AcademicYear.objects.get(id=year_id)
            AcademicYear.objects.filter(is_current=True).update(is_current=False)
            year.is_current = True
            year.save()
            return Response({'message': 'Current year set successfully'})
        except AcademicYear.DoesNotExist:
            return Response({'error': 'Academic year not found'}, status=status.HTTP_404_NOT_FOUND)

class SemesterViewSet(viewsets.ModelViewSet):
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    
    @action(detail=False, methods=['post'])
    def set_current(self, request):
        semester_id = request.data.get('semester_id')
        try:
            semester = Semester.objects.get(id=semester_id)
            Semester.objects.filter(is_current=True).update(is_current=False)
            semester.is_current = True
            semester.save()
            return Response({'message': 'Current semester set successfully'})
        except Semester.DoesNotExist:
            return Response({'error': 'Semester not found'}, status=status.HTTP_404_NOT_FOUND)

class AdmittedStudentViewSet(viewsets.ModelViewSet):
    queryset = AdmittedStudent.objects.all()
    serializer_class = AdmittedStudentSerializer
    permission_classes = [IsAuthenticated, IsStaff]
    
    @action(detail=False, methods=['post'])
    def confirm_enrollment(self, request):
        student_id = request.data.get('student_id')
        try:
            admitted = AdmittedStudent.objects.get(student_id=student_id)
            admitted.confirmed_enrollment = True
            admitted.confirmed_enrollment_date = timezone.now().date()
            admitted.save()
            return Response({'message': 'Enrollment confirmed'})
        except AdmittedStudent.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def pending_confirmations(self, request):
        pending = AdmittedStudent.objects.filter(confirmed_enrollment=False)
        serializer = AdmittedStudentSerializer(pending, many=True)
        return Response(serializer.data)