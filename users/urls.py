from django.urls import path
from .views import login_view, register_view, create_staff, staff_list, update_staff, branch_list, create_branch, update_branch_view, update_admin_profile, assign_staff_to_branch, admin_dashboard, staff_dashboard, client_page
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('register/', register_view, name='register' ),
    path('login/', login_view, name='login'),
    path('staff/all/', staff_list, name='staff_list' ),
    path('add/staff/', create_staff, name='create_staff' ),
    path('update/staff/<int:staff_id>/', update_staff, name='update_staff' ),
    path('branch/all/', branch_list, name='branch_list' ),
    path('create/branch/', create_branch, name='create_branch' ),
    path('update/branch/<int:branch_id>/', update_branch_view, name='update_branch' ),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('staff-dashboard/', staff_dashboard, name='staff_dashboard'),
    path('client/', client_page, name='client_page'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
]