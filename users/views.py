from django.shortcuts import render, redirect, get_object_or_404
from django.core import serializers
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Business, Branch
from shipments.models import Shipment
from clients.models import Client
from django.http import HttpResponseForbidden
from django.core.exceptions import ValidationError
from datetime import datetime
from functools import wraps
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

# logic for role based access
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
 
 
 # branch list
@login_required
@role_required('admin')
def branch_list(request):
    branches = Branch.objects.all()
     # Ensure only the client who created the shipment or an admin/staff can view it
    if not request.user.is_authenticated:
        return render(request, '403.html', {'error': 'You are not authorized to view this shipment'})
    return render(request, 'branch/branch_list.html', {'branches': branches})  

# register new business account
def register_view(request):
    if request.user.is_authenticated:
        # Redirect already authenticated users to their respective dashboards
        if request.user.role == 'admin':
            return redirect('admin_dashboard')
        elif request.user.role == 'staff':
            return redirect('staff_dashboard')
        
    if request.method == 'POST':
        # Extract user info
        firstname = request.POST['first_name']
        lastname = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        role = request.POST.get('role', 'admin')
        #get the branchid
        branch_id = request.POST.get('branch_id')
        branch = None
        # query the specific branch
        if branch_id:
            try:
                branch = Branch.objects.get(id=branch_id)
            except Branch.DoesNotExist:
                return render(request, 'users/signup.html', {'error': 'Invalid branch selected'})

        # Simple check for username uniqueness
        if CustomUser.objects.filter(username=username).exists():
            return render(request, 'users/signup.html', {'error': 'Username already exists'})
        
        if role == 'staff':
            # Create the new user. Note: first_name and last_name are already in AbstractUser.
            user = CustomUser.objects.create(
                first_name=firstname,
                last_name=lastname,
                username=username,
                email=email,
                password=make_password(password),
                role=role,
                #pass the branch as a foreign key to the user
                branch=branch
            )
        else:
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
            
            business.save() 
            # generate a token or perform additional st.
            return redirect('admin_dashboard')
        
        elif user.role == 'staff':
            return redirect('staff_dashboard')
        else:
            return redirect('client_page')
    
    return render(request, 'users/signup.html')

# render login page        
def login_view(request):
    if request.user.is_authenticated:
        # Redirect already authenticated users to their respective dashboards
        if request.user.role == 'admin':
            return redirect('admin_dashboard')
        elif request.user.role == 'staff':
            return redirect('staff_dashboard')
        
    if request.method == 'POST':
        username_or_email = request.POST['username']
        password = request.POST['password']
        
        # Try to authenticate with username first
        user = authenticate(request, username=username_or_email, password=password)
        
        # If authentication with username fails, try with email
        if user is None:
            try:
                user_obj = CustomUser.objects.get(email=username_or_email)
                user = authenticate(request, username=user_obj.username, password=password)
            except CustomUser.DoesNotExist:
                pass
        
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

# staff list
@login_required
@role_required('admin')
def staff_list(request):
    staffs = CustomUser.objects.filter(role='staff')
    # Ensure only authenticated users can view the staff list
    if not request.user.is_authenticated:
        return render(request, '403.html', {'error': 'You are not authorized to view this page'})
    return render(request, 'staff/staff_list.html', {'staffs': staffs})

# update staff  
@login_required
def update_staff(request, staff_id):
    # Ensure only admin can update staff
    if not request.user.is_authenticated:
        return HttpResponseForbidden()
    
    try:
        staff = CustomUser.objects.get(id=staff_id, role='staff')
    except CustomUser.DoesNotExist:
        return render(request, '404.html', {'error': 'Staff member not found'})
    
    branch_object = Branch.objects.all()
    
    if request.method == 'POST':
        # Extract updated user info
        firstname = request.POST.get('first_name', staff.first_name)
        lastname = request.POST.get('last_name', staff.last_name)
        email = request.POST.get('email', staff.email)
        branch_id = request.POST.get('branch_id')
        
        # Update branch if provided
        if branch_id:
            try:
                branch = Branch.objects.get(id=branch_id)
                staff.branch = branch
            except Branch.DoesNotExist:
                return render(request, 'staff/update_staff.html', {
                    'staff': staff,
                    'branch': branch_object,
                    'error': 'Invalid branch selected'
                })
        
        # Update staff details
        staff.first_name = firstname
        staff.last_name = lastname
        staff.email = email
        staff.save()
        
        return redirect('staff_list')
    
    return render(request, 'staff/update_staff.html', {
        'staff': staff,
        'branch': branch_object
    })

# create new staff
@login_required
def create_staff(request):
    branch_object = Branch.objects.all();
    if request.method == 'POST':
        # Extract user info
        firstname = request.POST['first_name']
        lastname = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        role = 'staff'
        username = f"{firstname.strip().lower()}{lastname.strip().lower()}"

        #get the branchid
        branch_id = request.POST.get('branch_id')
        branch = None
        # query the specific branch
        if branch_id:
            try:
                branch = Branch.objects.get(id=branch_id)
            except Branch.DoesNotExist:
                return render(request, 'users/signup.html', {'error': 'Invalid branch selected'})

        
        if role == 'staff':
            # Create the new user. Note: first_name and last_name are already in AbstractUser.
            user = CustomUser.objects.create(
                username=username,
                first_name=firstname,
                last_name=lastname,
                email=email,
                password=make_password(password),
                role=role,
                #pass the branch as a foreign key to the user
                branch=branch
            )
            user.save()                 
                
            return redirect('staff_list')
       
    
    return render(request, 'staff/create_staff.html', {'branch': branch_object})

# update the admin/business profile
@login_required
@role_required('admin')
def update_admin_profile(request):
    # Get current user and their business
    user = request.user
    if not user.is_authenticated or user.role != 'admin':
        return HttpResponseForbidden()
    
    current_business = Business.objects.get(owner=user)
    business_id = current_business.id
    business = get_object_or_404(Business, id=business_id)

    if request.method == 'POST':
        # Update User Information
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        
        # Handle password change
        new_password = request.POST.get('password')
        if new_password:
            user.set_password(new_password)
        
        # Update Business Information
        if business:
            business.name = request.POST.get('business_name', business.name)
            
            # Handle date conversion
            start_date_str = request.POST.get('start_date')
            if start_date_str:
                try:
                    business.start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                except ValueError:
                    messages.error(request, 'Invalid date format. Use YYYY-MM-DD.')
                    return redirect('update_admin_profile')
            
            # Handle file upload
            if 'business_logo' in request.FILES:
                business.business_logo = request.FILES['business_logo']
            
            # Update other business fields
            business_fields = [
                'currency_id', 'website', 'mobile', 'alternate_number',
                'country', 'state', 'city', 'zip_code', 'landmark', 'time_zone',
                'tax_label_1', 'tax_number_1', 'tax_label_2', 'tax_number_2',
                'fy_start_month', 'accounting_method'
            ]
            
            for field in business_fields:
                if field in request.POST:
                    setattr(business, field, request.POST.get(field))
        
        try:
            with transaction.atomic():
                user.save()
                if business:
                    business.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('admin_dashboard')
        
        except ValidationError as e:
            messages.error(request, f'Error updating profile: {e}')
        except Exception as e:
            messages.error(request, 'An error occurred while updating your profile')
            # Log the actual error for debugging
            logger.error(f"Error updating admin profile: {str(e)}")
            

    return render(request, 'business/update_profile.html', {
        'user': user,
        'business': business,
        'accounting_methods': Business.accounting_method,
    })

# create a new branch
@login_required
@role_required('admin')
def create_branch(request):
    if request.method == 'POST':
        #business_id = request.POST.get('business_id')
        branch_name = request.POST.get('branch_name')
        currency_id = request.POST.get('currency_id', 0)
        mobile = request.POST.get('mobile')
        alternate_number = request.POST.get('alternate_number')
        country = request.POST.get('country', '')
        state = request.POST.get('state', '')
        city = request.POST.get('city', '')
        zip_code = request.POST.get('zip_code', '')
        landmark = request.POST.get('landmark', '')
        time_zone = request.POST.get('time_zone', '')
        
        user = request.user
        current_business = Business.objects.get(owner=user)
        business_id = current_business.id

        # Only proceed if business_id is given
        if business_id:
            business = get_object_or_404(Business, id=business_id)

            if user.role == 'admin':
                branch = Branch.objects.create(
                    name=branch_name,
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
                branch.save()
                return redirect('branch_list')
        else:
            # Handle case where business_id is missing in POST
            return render(request, 'branch/create_branch.html', {
                'error_message': 'Business ID is required.'
            })

    # For GET request, just render the form
    return render(request, 'branch/create_branch.html')

# update the branch 
@login_required
@role_required('admin')
def update_branch_view(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    
    # Ensure only business admins can update branches
    if not request.user.is_authenticated or request.user.role != 'admin':
        return HttpResponseForbidden()

    if request.method == 'POST':
        branch.name = request.POST.get('branch_name', branch.name)
        branch.currency_id = request.POST.get('currency_id', branch.currency_id)
        branch.mobile = request.POST.get('mobile', branch.mobile)
        branch.alternate_number = request.POST.get('alternate_number', branch.alternate_number)
        branch.country = request.POST.get('country', branch.country)
        branch.state = request.POST.get('state', branch.state)
        branch.city = request.POST.get('city', branch.city)
        branch.zip_code = request.POST.get('zip_code', branch.zip_code)
        branch.landmark = request.POST.get('landmark', branch.landmark)
        branch.time_zone = request.POST.get('time_zone', branch.time_zone)
        
        branch.save()
        messages.success(request, 'Branch updated successfully')
        return redirect('branch_list')

    return render(request, 'branch/update_branch.html', {
        'branch': branch,
        'business': branch.business
    })

# assign staff to branch
@login_required    
def assign_staff_to_branch(request):
    if request.method == 'POST':
        staff_id = request.POST['staff_id']
        branch_id = request.POST['branch_id']
        
        staff = CustomUser.objects.get(id=staff_id, business=request.user.business)
        branch = Branch.objects.get(id=branch_id, business=request.user.business)
        
        staff.branch = branch
        staff.save()  # Business auto-assigned via save() method


# render the admin dashboard
@login_required
@role_required('admin')
def admin_dashboard(request):
    user = request.user

    # Safely get the business or return 404 if not found
    business = get_object_or_404(Business, owner=user)

    # Get shipments and clients related to the business
    shipments = Shipment.objects.filter(business=business, shipment_complete=False)
    clients = Client.objects.filter(business=business)
    
    # Convert QuerySets to JSON-compatible format
    shipments_json = serializers.serialize('json', shipments)
    clients_json = serializers.serialize('json', clients)

    context = {
        'business': business,
        'shipments': shipments,
        'shipments_json': shipments_json,
        'clients': clients,
        'total_shipments': shipments.count(),
        'total_clients': clients.count(),
    }

    return render(request, 'dash/admin_dashboard.html', context)

# render the staff dashboard
@login_required
@role_required('staff')
def staff_dashboard(request):
    user = request.user
    if user:
        branch = user.branch
        business_id = branch.business.id
        business = get_object_or_404(Business, id=business_id)
        
    shipments = Shipment.objects.filter(business=business, shipment_complete=False)
    clients = Client.objects.filter(business=business)
    total_clients = clients.count()
    total_shipments = shipments.count()
    return render(request, 'dash/staff_dashboard.html', {
        'shipments': shipments,
        'clients': clients, 
        'business': business, 
        'total_shipments': total_shipments,
        'total_clients': total_clients
    })

@login_required
@role_required('client')
def client_page(request):
    return render(request, 'dash/client_dashboard.html')

    