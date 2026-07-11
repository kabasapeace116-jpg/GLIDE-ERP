# core/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AuthViewSet, UserViewSet, DepartmentViewSet, CourseViewSet,
    ClassViewSet, StudentViewSet, StudentApplicationViewSet, 
    CourseCategoryViewSet, InvoiceViewSet,
    login_view, logout_view
)

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'users', UserViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'course-categories', CourseCategoryViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'classes', ClassViewSet)
router.register(r'students', StudentViewSet)
router.register(r'applications', StudentApplicationViewSet)
router.register(r'invoices', InvoiceViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('login/', login_view, name='login_fallback'),
    path('logout/', logout_view, name='logout_fallback'),
]