from django.urls import path
from .views import (
    getall_shipment, generate_shipment_receipt, shipment_tracker, createshipment_view, 
    shipment_detail, update_shipment, track_shipment, generate_invoice, #invoice_detail, 
    generate_invoice_pdf, delete_shipment, InvoiceDetailView, generate_invoice_pdf, 
    UpdatePaymentStatusView, ClientLedgerView, mark_shipment_complete
    )
urlpatterns = [
    #track shipment urls
    #path('', track_shipment, name='home'),
    path('track/', track_shipment, name='track_shipment'),
    path('track/shipment', shipment_tracker, name='shipment_tracker'),
    # create shipment
    path('create/', createshipment_view, name='create_shipment'),
    # shipment list
    path('all/', getall_shipment, name='getall_shipment'),
    # shipment details
    path('<int:shipment_id>/', shipment_detail, name='shipment_detail'),
    # update shipment
    path('<int:shipment_id>/update/', update_shipment, name='update_shipment'),
    # delete shipment 
    path('delete/<int:shipment_id>/', delete_shipment, name='delete_shipment'),
    # mark shipment as complete
    path('shipments/<int:pk>/complete/', mark_shipment_complete, name='mark_shipment_complete'),
    # shipment receipt
    path('receipt/<int:shipment_id>/', generate_shipment_receipt, name='generate_receipt'),
    # generate invoice
    path('generate/invoice/<int:shipment_id>/', generate_invoice, name='invoice_generate'),
    # invoice detail
    path('invoices/<int:pk>/', InvoiceDetailView.as_view(), name='invoice_detail'),
    # download invoice pdf
    path('invoices/<int:pk>/pdf/', generate_invoice_pdf, name='invoice_pdf'),
    # update payment status
    path('invoices/<int:pk>/update/', UpdatePaymentStatusView.as_view(), name='update_payment'),
    # client ledger
    path('clients/<int:pk>/ledger/', ClientLedgerView.as_view(), name='client_ledger'),
    

    #path('invoices/update/<int:pk>/paymentstatus/', update_payment, name='update_payment_status'),
    #path('invoices/generate/<int:shipment_id>/', generate_invoice, name='generate_invoice'),
    #path('invoices/<int:invoice_id>/', invoice_detail, name='invoice_detail'),
]
