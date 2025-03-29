from django.urls import path
from .views import client_list, client_detail, update_client, create_client

urlpatterns = [
    path('new/', create_client, name='create_client'),
    path('all/', client_list, name='client_list'),
    path('details/<int:pk>/', client_detail, name='client_detail'),
    path('update/<int:pk>/edit/', update_client, name='update_client'),
]
