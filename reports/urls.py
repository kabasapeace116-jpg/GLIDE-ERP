from django.urls import path
from .views import ReportViewSet

urlpatterns = [
    path('student-statistics/', ReportViewSet.as_view({'get': 'student_statistics'}), name='student-statistics'),
    path('academic-performance/', ReportViewSet.as_view({'get': 'academic_performance'}), name='academic-performance'),
    path('financial-summary/', ReportViewSet.as_view({'get': 'financial_summary'}), name='financial-summary'),
    path('attendance-summary/', ReportViewSet.as_view({'get': 'attendance_summary'}), name='attendance-summary'),
    path('course-enrollment/', ReportViewSet.as_view({'get': 'course_enrollment'}), name='course-enrollment'),
    path('generate-pdf/', ReportViewSet.as_view({'get': 'generate_pdf'}), name='generate-pdf'),
]