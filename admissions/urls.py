from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AcademicYearViewSet, SemesterViewSet, AdmittedStudentViewSet

router = DefaultRouter()
router.register(r'academic-years', AcademicYearViewSet, basename='academic-year')
router.register(r'semesters', SemesterViewSet, basename='semester')
router.register(r'admitted-students', AdmittedStudentViewSet, basename='admitted-student')

urlpatterns = [
    path('', include(router.urls)),
]