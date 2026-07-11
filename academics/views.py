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