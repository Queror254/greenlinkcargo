from django.urls import path
from .views import login_view, register_view, admin_dashboard, staff_dashboard, client_page
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('register/', register_view, name='register' ),
    path('login/', login_view, name='login'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('staff-dashboard/', staff_dashboard, name='staff_dashboard'),
    path('client/', client_page, name='client_page'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
]