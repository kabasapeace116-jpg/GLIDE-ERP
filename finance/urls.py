from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.views.generic import TemplateView
from .views import (
    FeeStructureViewSet, InvoiceViewSet, 
    PaymentViewSet, FinancialClearanceViewSet
)

router = DefaultRouter()
router.register(r'fee-structures', FeeStructureViewSet, basename='fee-structure')
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'clearance', FinancialClearanceViewSet, basename='clearance')

urlpatterns = [
    path('', include(router.urls)),
    # Template Views for Frontend
    path('invoices/', TemplateView.as_view(template_name='finance/invoices.html'), name='invoices_list'),
    path('invoices/<int:pk>/', TemplateView.as_view(template_name='finance/invoice_detail.html'), name='invoice_detail'),
    path('clearance/<int:pk>/', TemplateView.as_view(template_name='finance/clearance_detail.html'), name='clearance_detail'),
]