from django.db import models
from core.models import Student, Course, User
from admissions.models import Semester
from django.utils import timezone

class FeeStructure(models.Model):
    FEE_TYPES = (
        ('tuition', 'Tuition Fee'),
        ('application', 'Application Fee'),
        ('registration', 'Registration Fee'),
        ('exam', 'Examination Fee'),
        ('library', 'Library Fee'),
        ('activity', 'Activity Fee'),
        ('other', 'Other'),
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='fee_structures')
    fee_type = models.CharField(max_length=20, choices=FEE_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    academic_year = models.CharField(max_length=20)
    semester = models.CharField(max_length=10, blank=True)
    is_required = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('course', 'fee_type', 'academic_year', 'semester')

    def __str__(self):
        return f"{self.course.name} - {self.get_fee_type_display()} - {self.amount}"

# finance/models.py

class Invoice(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('issued', 'Issued'),
        ('partially_paid', 'Partially Paid'),
        ('fully_paid', 'Fully Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    )
    invoice_number = models.CharField(max_length=20, unique=True)
    student = models.ForeignKey('core.Student', on_delete=models.CASCADE, related_name='invoices')
    semester = models.ForeignKey('admissions.Semester', on_delete=models.CASCADE, related_name='invoices')
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.balance = self.total_amount - self.amount_paid
        if self.balance <= 0:
            self.status = 'fully_paid'
        elif self.balance > 0 and self.status != 'draft':
            self.status = 'partially_paid'
        if not self.invoice_number:
            year = timezone.now().year
            last_inv = Invoice.objects.filter(
                invoice_number__startswith=f"INV/{year}"
            ).order_by('-invoice_number').first()
            if last_inv:
                seq = int(last_inv.invoice_number.split('/')[-1]) + 1
            else:
                seq = 1
            self.invoice_number = f"INV/{year}/{seq:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice_number} - {self.student.registration_number}"


class Payment(models.Model):
    PAYMENT_METHODS = (
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
        ('mobile', 'Mobile Money'),
        ('card', 'Card Payment'),
        ('cheque', 'Cheque'),
        ('other', 'Other'),
    )
    payment_number = models.CharField(max_length=20, unique=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    reference_number = models.CharField(max_length=50, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    bank_branch = models.CharField(max_length=100, blank=True)
    receipt_number = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.payment_number:
            year = timezone.now().year
            last_pay = Payment.objects.filter(
                payment_number__startswith=f"PAY/{year}"
            ).order_by('-payment_number').first()
            if last_pay:
                seq = int(last_pay.payment_number.split('/')[-1]) + 1
            else:
                seq = 1
            self.payment_number = f"PAY/{year}/{seq:04d}"
        super().save(*args, **kwargs)
        # Update invoice amount paid
        self.invoice.amount_paid = self.invoice.payments.aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        self.invoice.save()

    def __str__(self):
        return f"{self.payment_number} - {self.student.registration_number} - {self.amount}"

class FinancialClearance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='financial_clearances')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='financial_clearances')
    is_cleared = models.BooleanField(default=False)
    clearance_date = models.DateField(null=True, blank=True)
    cleared_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='cleared_students')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'semester')

    def __str__(self):
        return f"{self.student.registration_number} - {self.semester} - {'Cleared' if self.is_cleared else 'Not Cleared'}"