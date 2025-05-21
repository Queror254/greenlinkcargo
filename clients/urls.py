from django.urls import path
from .views import client_list, client_detail, update_client, create_client, delete_client

urlpatterns = [
    # create new client
    path('new/', create_client, name='create_client'),
    # fetch all clients
    path('all/', client_list, name='client_list'),
    # view client details page
    path('details/<int:pk>/', client_detail, name='client_detail'),
    # update the client
    path('update/<int:pk>/edit/', update_client, name='update_client'),
    # delete client
    path('delete/<int:pk>/', delete_client, name='delete_client'),
]
