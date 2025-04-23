from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Business
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
   
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from django.contrib.auth import login as auth_login
from .models import CustomUser, Business

def register_view(request):
    if request.method == 'POST':
        # Extract user info
        firstname = request.POST['first_name']
        lastname = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        role = request.POST.get('role', 'admin')  # Default role to 'client' if not provided

        # Simple check for username uniqueness
        if CustomUser.objects.filter(username=username).exists():
            return render(request, 'users/register.html', {'error': 'Username already exists'})

        # Create the new user. Note: first_name and last_name are already in AbstractUser.
        user = CustomUser.objects.create(
            first_name=firstname,
            last_name=lastname,
            username=username,
            email=email,
            password=make_password(password),
            role=role
        )

        # Log in the new user
        auth_login(request, user)
        
        # For an admin/owner account, create and link the Business record.
        if user.role == 'admin':
            # Extract business-related fields from the POST data. Adjust field names as needed.
            business_name    = request.POST.get('business_name')
            start_date       = request.POST.get('start_date')  # May need conversion to date
            currency_id      = request.POST.get('currency_id', 0)
            business_logo = request.FILES.get('business_logo')
            website          = request.POST.get('website')
            mobile           = request.POST.get('mobile')
            alternate_number = request.POST.get('alternate_number')
            country          = request.POST.get('country', '')
            state            = request.POST.get('state', '')
            city             = request.POST.get('city', '')
            zip_code         = request.POST.get('zip_code', '')
            landmark         = request.POST.get('landmark', '')
            time_zone        = request.POST.get('time_zone', '')
            tax_label_1        = request.POST.get('tax_label_1', '')
            tax_number_1        = request.POST.get('tax_number_1', '')
            tax_label_2        = request.POST.get('tax_label_2', '')
            tax_number_2        = request.POST.get('tax_number_2', '')
            financialyear_start_month        = request.POST.get('fy_start_month', '')
            accounting_method        = request.POST.get('accounting_method', '')
            # You can extract other fields (taxs, accounting_method, etc.) similarly.
            
            # Create and link the Business record.
            business = Business.objects.create(
                name=business_name,
                start_date=start_date or None,
                currency_id=currency_id,
                business_logo=business_logo or None,
                website=website,
                mobile=mobile,
                alternate_number=alternate_number,
                country=country,
                state=state,
                city=city,
                zip_code=zip_code,
                landmark=landmark,
                time_zone=time_zone,
                tax_label_1=tax_label_1,
                tax_number_1=tax_number_1,
                tax_label_2=tax_label_2,
                tax_number_2=tax_number_2,
                fy_start_month=financialyear_start_month,
                accounting_method=accounting_method,
                owner=user  # This links the business to the user (owner)
            )
            # generate a token or perform additional st.
            return redirect('admin_dashboard')
        
        elif user.role == 'staff':
            return redirect('staff_dashboard')
        else:
            return redirect('client_page')
    
    return render(request, 'users/signup.html')

def create_branch(request):
    business_id = request.POST.get('client')
    if business_id:
        business = get_object_or_404(Business, id=business_id)
    
    business_name    = request.POST.get('business_name')
    currency_id      = request.POST.get('currency_id', 0)
    mobile           = request.POST.get('mobile')
    alternate_number = request.POST.get('alternate_number')
    country          = request.POST.get('country', '')
    state            = request.POST.get('state', '')
    city             = request.POST.get('city', '')
    zip_code         = request.POST.get('zip_code', '')
    landmark         = request.POST.get('landmark', '')
    time_zone        = request.POST.get('time_zone', '')
    
    
    business = Business.objects.create(
        name=business_name,
        currency_id=currency_id,
        mobile=mobile,
        alternate_number=alternate_number,
        country=country,
        state=state,
        city=city,
        zip_code=zip_code,
        landmark=landmark,
        time_zone=time_zone,
        business=business
    )
    
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

    