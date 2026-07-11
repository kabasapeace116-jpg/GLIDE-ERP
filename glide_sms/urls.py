from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView
from django.views.generic import RedirectView

# ALL DRF_YASG IMPORTS REMOVED

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Public Pages
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='/login/'), name='logout'),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('contact/', TemplateView.as_view(template_name='contact.html'), name='contact'),
    path('governance/', TemplateView.as_view(template_name='governance.html'), name='governance'),
    path('staff/', TemplateView.as_view(template_name='staff.html'), name='staff'),
    path('terms/', TemplateView.as_view(template_name='terms.html'), name='terms'),
    path('privacy/', TemplateView.as_view(template_name='privacy.html'), name='privacy'),
    path('faq/', TemplateView.as_view(template_name='faq.html'), name='faq'),
    
    # Dashboard Pages
    path('dashboard/student/', TemplateView.as_view(template_name='dashboard/student_dashboard.html'), name='student_dashboard'),
    path('dashboard/admin/', TemplateView.as_view(template_name='dashboard/admin_dashboard.html'), name='admin_dashboard'),
    path('dashboard/finance/', TemplateView.as_view(template_name='dashboard/finance_dashboard.html'), name='finance_dashboard'),
    path('dashboard/staff/', TemplateView.as_view(template_name='dashboard/staff_dashboard.html'), name='staff_dashboard'),
    path('dashboard/hr/', TemplateView.as_view(template_name='dashboard/hr_dashboard.html'), name='hr_dashboard'),
    
    # Admissions Pages
    path('admissions/', TemplateView.as_view(template_name='admissions/landing.html'), name='admissions_landing'),
    path('admissions/applications/', TemplateView.as_view(template_name='admissions/applications.html'), name='applications'),
    path('admissions/applications/<int:pk>/', TemplateView.as_view(template_name='admissions/application_detail.html'), name='application_detail'),
    path('admissions/register/', TemplateView.as_view(template_name='admissions/register_student.html'), name='register_student'),
    path('admissions/apply/', TemplateView.as_view(template_name='admissions/apply.html'), name='apply'),
    
    # Academics Pages
    path('academics/dashboard/', TemplateView.as_view(template_name='academics/dashboard.html'), name='academics_dashboard'),
    path('academics/courses/', TemplateView.as_view(template_name='academics/courses.html'), name='courses'),
    path('academics/courses/create/', TemplateView.as_view(template_name='academics/course_create.html'), name='course_create'),
    path('academics/courses/<int:pk>/', TemplateView.as_view(template_name='academics/course_detail.html'), name='course_detail'),
    path('academics/classes/', TemplateView.as_view(template_name='academics/classes.html'), name='classes'),
    path('academics/timetables/', TemplateView.as_view(template_name='academics/timetables.html'), name='timetables'),
    path('academics/timetables/create/', TemplateView.as_view(template_name='academics/timetable_create.html'), name='timetable_create'),
    path('academics/assessments/', TemplateView.as_view(template_name='academics/assessments.html'), name='assessments'),
    path('academics/assessments/create/', TemplateView.as_view(template_name='academics/assessment_create.html'), name='assessment_create'),
    path('academics/results/', TemplateView.as_view(template_name='academics/results.html'), name='results'),
    path('academics/results/<int:pk>/', TemplateView.as_view(template_name='academics/result_detail.html'), name='result_detail'),
    path('academics/results/upload/', TemplateView.as_view(template_name='academics/result_upload.html'), name='result_upload'),
    path('academics/attendance/', TemplateView.as_view(template_name='academics/attendance.html'), name='attendance'),
    path('academics/attendance/record/', TemplateView.as_view(template_name='academics/attendance_record.html'), name='attendance_record'),
    
    # Finance Pages
    path('finance/', RedirectView.as_view(url='/dashboard/finance/', permanent=True), name='finance_redirect'),
    path('finance/fees/', TemplateView.as_view(template_name='finance/fees.html'), name='fees'),
    path('finance/fees/add/', TemplateView.as_view(template_name='finance/fee_add.html'), name='fee_add'),
    path('finance/fees/<int:pk>/edit/', TemplateView.as_view(template_name='finance/fee_edit.html'), name='fee_edit'),
    path('finance/invoices/', TemplateView.as_view(template_name='finance/invoices.html'), name='invoices'),
    path('finance/invoices/<int:pk>/', TemplateView.as_view(template_name='finance/invoice_detail.html'), name='finance_invoice_detail'),
    path('finance/invoices/generate/', TemplateView.as_view(template_name='finance/invoice_generate.html'), name='invoice_generate'),
    path('finance/payments/', TemplateView.as_view(template_name='finance/payments.html'), name='payments'),
    path('finance/payments/record/', TemplateView.as_view(template_name='finance/payment_record.html'), name='payment_record'),
    path('finance/clearance/', TemplateView.as_view(template_name='finance/clearance.html'), name='clearance'),
    path('finance/clearance/<int:pk>/', TemplateView.as_view(template_name='finance/clearance_detail.html'), name='finance_clearance_detail'),
    
    # HR Pages
    path('hr/', TemplateView.as_view(template_name='hr/dashboard.html'), name='hr_dashboard'),
    path('hr/dashboard/', TemplateView.as_view(template_name='hr/dashboard.html'), name='hr_dashboard_redirect'),
    path('hr/employees/', TemplateView.as_view(template_name='hr/employees.html'), name='hr_employees'),
    path('hr/employees/add/', TemplateView.as_view(template_name='hr/employee_add.html'), name='hr_employee_add'),
    path('hr/employees/<int:pk>/', TemplateView.as_view(template_name='hr/employee_detail.html'), name='hr_employee_detail'),
    path('hr/employees/<int:pk>/edit/', TemplateView.as_view(template_name='hr/employee_edit.html'), name='hr_employee_edit'),
    path('hr/leave-requests/', TemplateView.as_view(template_name='hr/leave_requests.html'), name='hr_leave_requests'),
    path('hr/attendance/', TemplateView.as_view(template_name='hr/attendance.html'), name='hr_attendance'),
    path('hr/reports/', TemplateView.as_view(template_name='hr/hr_reports.html'), name='hr_reports'),
    
    # Reports Pages
    path('reports/', TemplateView.as_view(template_name='reports/reports.html'), name='reports'),
    path('reports/student-statistics/', TemplateView.as_view(template_name='reports/student_statistics.html'), name='student_statistics'),
    path('reports/academic-performance/', TemplateView.as_view(template_name='reports/academic_performance.html'), name='academic_performance'),
    path('reports/financial-summary/', TemplateView.as_view(template_name='reports/financial_summary.html'), name='financial_summary'),
    path('reports/attendance-summary/', TemplateView.as_view(template_name='reports/attendance_summary.html'), name='attendance_summary'),
    path('reports/course-enrollment/', TemplateView.as_view(template_name='reports/course_enrollment.html'), name='course_enrollment'),
    path('reports/generate-pdf/', TemplateView.as_view(template_name='reports/generate_pdf.html'), name='generate_pdf'),
    
    # Students
    path('students/', TemplateView.as_view(template_name='students/all_students.html'), name='all_students'),
    path('students/<int:pk>/edit/', TemplateView.as_view(template_name='students/student_edit.html'), name='student_edit'),
    path('students/<int:pk>/', TemplateView.as_view(template_name='students/student_detail.html'), name='student_detail'),
    path('test-edit/', TemplateView.as_view(template_name='students/student_edit.html'), name='test_edit'),
    
    # User Management
    path('users/', TemplateView.as_view(template_name='users/user_management.html'), name='user_management'),
    
    # API URLs
    path('api/', include('core.urls')),
    path('api/admissions/', include('admissions.urls')),
    path('api/academics/', include('academics.urls')),
    path('api/finance/', include('finance.urls')),
    path('api/hr/', include('hr.urls')),
    path('api/reports/', include('reports.urls')),
    
    # SWAGGER/REDOC URLS COMPLETELY REMOVED
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
