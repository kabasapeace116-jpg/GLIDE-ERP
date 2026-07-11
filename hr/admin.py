from django.contrib import admin
from .models import Employee, LeaveRequest, Attendance

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_number', 'user', 'department', 'position', 'employment_type', 'status')
    list_filter = ('department', 'employment_type', 'status')
    search_fields = ('employee_number', 'user__username', 'user__first_name', 'user__last_name')

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'start_date', 'end_date', 'status')
    list_filter = ('leave_type', 'status')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'check_in_time', 'check_out_time', 'is_late', 'is_absent')
    list_filter = ('is_late', 'is_absent', 'date')