from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import FormView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, HttpResponseForbidden
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from .models import Rates, Taxes, Additionalcosts
from .forms import TaxesForm, AdditionalCostsForm, AdditionalCostFormSet
from shipments.models import Shipment, Business

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
 
 
@login_required
@role_required('admin')
# permission management logic
def permissions(request):
    return render(request, 'permissions/permission_setting.html')
    
# Taxes Views
class TaxesListView(ListView):
    model = Taxes
    template_name = 'taxes/taxes_list.html'
    context_object_name = 'taxes'

# create new taxes
class TaxesCreateView(CreateView):
    model = Taxes
    form_class = TaxesForm
    template_name = 'taxes/taxes_form.html'
    success_url = reverse_lazy('taxes-list')

# update taxes
class TaxesUpdateView(UpdateView):
    model = Taxes
    form_class = TaxesForm
    template_name = 'taxes/taxes_form.html'
    success_url = reverse_lazy('taxes-list')

# delete taxes
class TaxesDeleteView(DeleteView):
    model = Taxes
    template_name = 'taxes/taxes_confirm_delete.html'
    success_url = reverse_lazy('taxes-list')

# AdditionalCosts Views
class AdditionalCostsListView(ListView):
    model = Additionalcosts
    template_name = 'additionalcosts/additionalcosts_list.html'
    context_object_name = 'additional_costs'

# create additional cost
class AdditionalCostsCreateView(FormView):
    form_class = AdditionalCostFormSet
    template_name = 'additionalcosts/additionalcosts_form.html'
    success_url = reverse_lazy('getall_shipment')

    def get_form_kwargs(self):
        """Pass the shipment to each form in the formset"""
        kwargs = super().get_form_kwargs()
        kwargs['prefix'] = 'costs'
        shipment_id = self.request.GET.get('shipment_id')
        
        # Initialize form_kwargs if it doesn't exist
        if 'form_kwargs' not in kwargs:
            kwargs['form_kwargs'] = {}
            
        if shipment_id:
            try:
                shipment = get_object_or_404(Shipment, id=shipment_id)
                kwargs['form_kwargs']['shipment'] = shipment
            except (ValueError, Shipment.DoesNotExist):
                messages.warning(self.request, "Invalid shipment reference")
        
        kwargs['prefix'] = 'costs'  # Important for formset management
        return kwargs

    def form_valid(self, formset):
        """Handle valid formset submission"""
        shipment_id = self.request.GET.get('shipment_id')
        shipment = None
        
        if shipment_id:
            try:
                shipment = get_object_or_404(Shipment, id=shipment_id)
            except (ValueError, Shipment.DoesNotExist):
                messages.error(self.request, "Invalid shipment reference")
                return self.form_invalid(formset)
        
        # Save all forms in the formset
        instances = []
        for form in formset:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                instance = form.save(commit=False)
                if shipment:
                    instance.shipment = shipment
                instance.save()
                instances.append(instance)
        
        if not instances:
            messages.warning(self.request, "No additional costs were created")
        
        messages.success(self.request, f"Successfully created {len(instances)} additional costs")
        return super().form_valid(formset)

    def get_success_url(self):
        """Optionally redirect back to shipment detail if came from there"""
        default_url = super().get_success_url()
        shipment_id = self.request.GET.get('shipment_id')
        
        if shipment_id and 'from_shipment' in self.request.GET:
            return reverse('shipment-detail', kwargs={'pk': shipment_id})
        
        return default_url
        
# update additional cost
class AdditionalCostsUpdateView(UpdateView):
    model = Additionalcosts
    form_class = AdditionalCostsForm
    template_name = 'additionalcosts/additionalcosts_form.html'
    success_url = reverse_lazy('getall_shipment')

# delete additional cost
class AdditionalCostsDeleteView(DeleteView):
    model = Additionalcosts
    template_name = 'additionalcosts/additionalcosts_confirm_delete.html'
    success_url = reverse_lazy('additionalcosts-list')


#def business_settings(request):
#    rates = Rates.objects.first()  # Assuming one rate record exists
#    return render(request, "settings/shipping_rates.html", {"rates": rates})

# shipping rate settings
@login_required
@role_required('admin')
def shipping_rate_settings(request):
    # fetch rates
    rates = Rates.objects.all()
    context = {
        'rates': rates,
        'page_title': 'Shipping Rate Settings'
    }
    return render(request, 'settings/rates/shipping_rate_settings.html', context)

# create shipping rate
@login_required
@role_required('admin')
def create_shipping_rate(request):
    # get the current logged in user: 
    user = request.user
    business = None
    
    if user.role == 'admin':
        # fetch the business directly
        business = get_object_or_404(Business, owner=user)
    elif user.role == 'staff':
        # fetch the business from the branch
        branch = user.branch
        business = branch.business
        
    if request.method == 'POST':
        name = request.POST.get('route_name')
        w_rate = request.POST.get('weight_rate')
        cbm_rate = request.POST.get('cbm_rate')
        
        try:
            shipping_rate = Rates.objects.create(
                business=business,
                route=name,
                weight_rate=w_rate,
                cbm_rate=cbm_rate,
            )
            shipping_rate.save()
            messages.success(request, "Shipping rate created successfully!")
            return redirect('shipping_rate_settings')
        except Exception as e:
            messages.error(request, f"Error creating shipping rate: {e}")
    
    return render(request, 'settings/rates/create_shipping_rate.html')

# update shipping rates
@login_required
@role_required('admin')
def update_shipping_rate(request, rate_id):
    rate = get_object_or_404(Rates, id=rate_id)
    
    if request.method == 'POST':
        route_name = request.POST.get('route_name')
        w_rate = request.POST.get('weight_rate')
        c_rate = request.POST.get('cbm_rate')
        
        try:
            rate.route = route_name
            rate.weight_rate = w_rate
            rate.cbm_rate = c_rate
            rate.save()
            messages.success(request, "Shipping rate updated successfully!")
            return redirect('shipping_rate_settings')
        except Exception as e:
            messages.error(request, f"Error updating shipping rate: {e}")
    
    context = {
        'rate': rate,
        'page_title': 'Edit Shipping Rate'
    }
    return render(request, 'settings/rates/edit_shipping_rate.html', context)

# delete shipping rates
@login_required
@role_required('admin')
def delete_shipping_rate(request, rate_id):
    rate = get_object_or_404(Rates, id=rate_id)
    
    try:
        rate.delete()
        messages.success(request, "Shipping rate deleted successfully!")
    except Exception as e:
        messages.error(request, f"Error deleting shipping rate: {e}")
    
    return redirect('shipping_rate_settings')

# update the weight rate
@login_required
@role_required('admin')
def update_weight_rate(request):
    if request.method == "POST":
        weight_rate = request.POST.get("weight_rate")
        try:
            rate_obj, created = Rates.objects.get_or_create(id=1)  # Assuming single rate row
            rate_obj.weight_rate = float(weight_rate)
            rate_obj.save()
            messages.success(request, "Weight rate updated successfully!")
        except Exception as e:
            messages.error(request, f"Error updating weight rate: {e}")

    return redirect('shipping_rate_settings')

# update the cbm rate
@login_required
@role_required('admin')
def update_cbm_rate(request):
    if request.method == "POST":
        cbm_rate = request.POST.get("cbm_rate")
        try:
            rate_obj, created = Rates.objects.get_or_create(id=1)
            rate_obj.cbm_rate = float(cbm_rate)
            rate_obj.save()
            messages.success(request, "CBM rate updated successfully!")
        except Exception as e:
            messages.error(request, f"Error updating CBM rate: {e}")

    return redirect('shipping_rate_settings')

