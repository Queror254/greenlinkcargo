from django.urls import path
from .views import update_weight_rate, update_cbm_rate, permissions
from users.views import update_admin_profile
from django.urls import path, include
from . import views

urlpatterns = [
    # permissions url under development
    path('permissions/', permissions, name='permission_settings'),
    # Shipping Rates urls
    path('rates/', views.shipping_rate_settings, name='shipping_rate_settings'),
    path('rates/create/', views.create_shipping_rate, name='create_shipping_rate'),
    path('rates/update/<int:rate_id>/', views.update_shipping_rate, name='update_shipping_rate'),
    path('rates/delete/<int:rate_id>/', views.delete_shipping_rate, name='delete_shipping_rate'),
    path('rates/update-weight/', views.update_weight_rate, name='update_weight_rate'),
    path('rates/update-cbm/', views.update_cbm_rate, name='update_cbm_rate'),

    # bussiness settings and rate settings
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
