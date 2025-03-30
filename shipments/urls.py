from django.urls import path
from .views import getall_shipment, shipment_tracker, createshipment_view, shipment_detail, update_shipment, track_shipment, generate_invoice, invoice_detail, generate_invoice_pdf, delete_shipment

urlpatterns = [
    path('', track_shipment, name='home'),
    path('track/', track_shipment, name='track_shipment'),
    path('track/shipment', shipment_tracker, name='shipment_tracker'),
    path('create/', createshipment_view, name='create_shipment'),
    path('all/', getall_shipment, name='getall_shipment'),
    path('<int:shipment_id>/', shipment_detail, name='shipment_detail'),
    path('<int:shipment_id>/update/', update_shipment, name='update_shipment'),
    path('delete/<int:shipment_id>/', delete_shipment, name='delete_shipment'),

    
    path('invoices/generate/<int:shipment_id>/', generate_invoice, name='generate_invoice'),
    path('invoices/<int:invoice_id>/', invoice_detail, name='invoice_detail'),
    path('invoices/pdf/<int:invoice_id>/', generate_invoice_pdf, name='generate_invoice_pdf'),
]
