from django.contrib import admin
from .models import FeeStructure, Invoice, Payment, FinancialClearance

@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ('course', 'fee_type', 'amount', 'academic_year', 'is_active')
    list_filter = ('fee_type', 'course', 'is_active')

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'student', 'total_amount', 'balance', 'status', 'due_date')
    list_filter = ('status', 'semester')
    search_fields = ('invoice_number', 'student__registration_number')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_number', 'student', 'amount', 'payment_date', 'payment_method')
    list_filter = ('payment_method', 'payment_date')
    search_fields = ('payment_number', 'student__registration_number')

@admin.register(FinancialClearance)
class FinancialClearanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'semester', 'is_cleared', 'clearance_date')
    list_filter = ('is_cleared', 'semester')
    search_fields = ('student__registration_number', 'student__first_name', 'student__last_name')