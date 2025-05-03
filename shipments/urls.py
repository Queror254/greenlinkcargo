from django.urls import path
from .views import (
    getall_shipment, generate_shipment_receipt, shipment_tracker, createshipment_view, 
    shipment_detail, update_shipment, track_shipment, #generate_invoice, invoice_detail, 
    generate_invoice_pdf, delete_shipment, InvoiceDetailView, generate_invoice_pdf, 
    UpdatePaymentStatusView, ClientLedgerView, mark_shipment_complete
    )
urlpatterns = [
    path('', track_shipment, name='home'),
    path('track/', track_shipment, name='track_shipment'),
    path('track/shipment', shipment_tracker, name='shipment_tracker'),
    path('create/', createshipment_view, name='create_shipment'),
    path('all/', getall_shipment, name='getall_shipment'),
    path('receipt/<int:shipment_id>/', generate_shipment_receipt, name='generate_receipt'),
    path('<int:shipment_id>/', shipment_detail, name='shipment_detail'),
    path('<int:shipment_id>/update/', update_shipment, name='update_shipment'),
    path('delete/<int:shipment_id>/', delete_shipment, name='delete_shipment'),
    path('invoices/<int:pk>/', InvoiceDetailView.as_view(), name='invoice_detail'),
    path('invoices/<int:pk>/pdf/', generate_invoice_pdf, name='invoice_pdf'),
    path('invoices/<int:pk>/update/', UpdatePaymentStatusView.as_view(), name='update_payment'),
    #path('invoices/update/<int:pk>/paymentstatus/', update_payment, name='update_payment_status'),
    path('clients/<int:pk>/ledger/', ClientLedgerView.as_view(), name='client_ledger'),
    path('shipments/<int:pk>/complete/', mark_shipment_complete, name='mark_shipment_complete'),

    
    #path('invoices/generate/<int:shipment_id>/', generate_invoice, name='generate_invoice'),
    #path('generate/invoice/<int:shipment_id>/', generate_invoice, name='invoice_generate'),
    #path('invoices/<int:invoice_id>/', invoice_detail, name='invoice_detail'),
    #path('invoices/pdf/<int:invoice_id>/', generate_invoice_pdf, name='generate_invoice_pdf'),
]
