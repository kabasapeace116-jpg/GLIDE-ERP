from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Admin permission - super_admin, admin, registrar"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type in ['super_admin', 'admin', 'registrar']


class IsSuperAdmin(BasePermission):
    """Super Admin only"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'super_admin'


class IsStaff(BasePermission):
    """Staff permission - any staff role"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type in ['super_admin', 'admin', 'staff', 'registrar', 'lecturer', 'finance', 'hr']


class IsStudent(BasePermission):
    """Student only"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'student'


class IsFinance(BasePermission):
    """Finance permission - admin, super_admin, finance"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type in ['admin', 'super_admin', 'finance']


class IsLecturer(BasePermission):
    """Lecturer only"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'lecturer'


class IsHR(BasePermission):
    """HR only"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'hr'


class IsRegistrar(BasePermission):
    """Registrar only"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'registrar'
