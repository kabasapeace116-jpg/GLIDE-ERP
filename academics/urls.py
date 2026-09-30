# academics/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CourseUnitViewSet,
    AssessmentViewSet,
    ResultViewSet,
    AttendanceRecordViewSet,
    TimetableViewSet,
    CertificateViewSet,
    VerifyCertificateView,
)

router = DefaultRouter()
router.register(r'course-units', CourseUnitViewSet, basename='course-unit')
router.register(r'assessments', AssessmentViewSet, basename='assessment')
router.register(r'results', ResultViewSet, basename='result')
router.register(r'attendance', AttendanceRecordViewSet, basename='attendance')
router.register(r'timetables', TimetableViewSet, basename='timetable')
router.register(r'certificates', CertificateViewSet, basename='certificate')

urlpatterns = [
    path(
        'certificates/verify/<uuid:verification_code>/',
        VerifyCertificateView.as_view(),
        name='api-verify-certificate',
    ),
    path('', include(router.urls)),
]