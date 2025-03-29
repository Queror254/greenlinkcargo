from django.contrib import admin
from .models import Shipment

@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'shipment_type', 'destination', 'status', 'created_at')
    list_filter = ('shipment_type', 'status', 'destination')
    search_fields = ('airwaybill', 'seawaybill', 'client__username')
