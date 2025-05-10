from django.urls import path
from .views import business_settings, update_weight_rate, update_cbm_rate
from users.views import update_admin_profile
from django.urls import path, include
from . import views

urlpatterns = [
    path("rates/", business_settings, name="business_settings"),
    path('business/', update_admin_profile, name="general_settings"),
    path("update-weight/", update_weight_rate, name="update_weight_rate"),
    path("update-cbm/", update_cbm_rate, name="update_cbm_rate"),
    
     # Taxes URLs
    path('taxes/', views.TaxesListView.as_view(), name='taxes-list'),
    path('taxes/create/', views.TaxesCreateView.as_view(), name='taxes-create'),
    path('taxes/<int:pk>/update/', views.TaxesUpdateView.as_view(), name='taxes-update'),
    path('taxes/<int:pk>/delete/', views.TaxesDeleteView.as_view(), name='taxes-delete'),
    
    # AdditionalCosts URLs
    path('additional-costs/', views.AdditionalCostsListView.as_view(), name='additionalcosts-list'),
    path('additional-costs/create/', views.AdditionalCostsCreateView.as_view(), name='additionalcosts-create'),
    path('additional-costs/<int:pk>/update/', views.AdditionalCostsUpdateView.as_view(), name='additionalcosts-update'),
    path('additional-costs/<int:pk>/delete/', views.AdditionalCostsDeleteView.as_view(), name='additionalcosts-delete'),
]
