# academics/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CourseUnitViewSet, AssessmentViewSet, ResultViewSet, 
    AttendanceRecordViewSet, TimetableViewSet
)

router = DefaultRouter()
router.register(r'course-units', CourseUnitViewSet, basename='course-unit')
router.register(r'assessments', AssessmentViewSet, basename='assessment')
router.register(r'results', ResultViewSet, basename='result')
router.register(r'attendance', AttendanceRecordViewSet, basename='attendance')
router.register(r'timetables', TimetableViewSet, basename='timetable')

urlpatterns = [
    path('', include(router.urls)),
]