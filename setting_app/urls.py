from django.urls import path
from .views import business_settings, update_weight_rate, update_cbm_rate

urlpatterns = [
    path("rates/", business_settings, name="business_settings"),
    path("update-weight/", update_weight_rate, name="update_weight_rate"),
    path("update-cbm/", update_cbm_rate, name="update_cbm_rate"),
]
