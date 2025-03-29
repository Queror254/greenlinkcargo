from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from .models import CustomUser
from shipments.models import Shipment
from clients.models import Client
from django.http import HttpResponseForbidden
from functools import wraps

def role_required(required_role):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("You must be logged in to access this page.", status=403)

            if hasattr(request.user, 'role') and request.user.role == required_role:
                return view_func(request, *args, **kwargs)
            
            return render(request, '403.html', status=403)
        
        return _wrapped_view
    return decorator
   
def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        #confirm_password = request.POST['confirm_password']
        role = request.POST.get('role', 'client')  # Default role to 'client' if not provided

        #if password != confirm_password:
        #    return render(request, 'users/register.html', {'error': 'Passwords do not match'})

        if CustomUser.objects.filter(username=username).exists():
            return render(request, 'users/register.html', {'error': 'Username already exists'})

        user = CustomUser.objects.create(
            username=username,
            password=make_password(password),
            role=role
        )

        auth_login(request, user)
        
        if user.role == 'admin':
            return redirect('admin_dashboard')
        elif user.role == 'staff':
            return redirect('staff_dashboard')
        else:
            return redirect('client_page')

    return render(request, 'users/register.html')
    
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            if user.role == 'admin':
                return redirect('admin_dashboard')
            elif user.role == 'staff':
                return redirect('staff_dashboard')
            else:
                return redirect('client_page')
        else:
            return render(request, 'users/login.html', {'error': 'Invalid credentials'})
    return render(request, 'users/login.html')

@login_required
@role_required('admin')
def admin_dashboard(request):
    shipments = Shipment.objects.all()
    clients = Client.objects.all()
    total_clients = Client.objects.count()
    total_shipments = Shipment.objects.count()
    return render(request, 'dash/admin_dashboard.html', {'shipments': shipments, 'clients': clients, 'total_shipments': total_shipments, 'total_clients': total_clients})

@login_required
@role_required('staff')
def staff_dashboard(request):
    shipments = Shipment.objects.all()
    return render(request, 'dash/staff_dashboard.html', {'shipments': shipments})

@login_required
@role_required('client')
def client_page(request):
    return render(request, 'dash/client_dashboard.html')

    