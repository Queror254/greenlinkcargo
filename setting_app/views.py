from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import FormView
from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Rates, Taxes, Additionalcosts
from .serializers import TaxesSerializer, AdditionalcostsSerializer
from .forms import TaxesForm, AdditionalCostsForm, AdditionalCostFormSet
from shipments.models import Shipment
#testing data visualization using matplotlib
def index(request):
    year=[2019,2020,2021,2022,2023]
    sales=[187.2,196.9,242,232.2,231.3]

    return render(request, "dataview/index.html", {'y': year, 's': sales})

# Taxes Views
class TaxesListView(ListView):
    model = Taxes
    template_name = 'taxes/taxes_list.html'
    context_object_name = 'taxes'

class TaxesCreateView(CreateView):
    model = Taxes
    form_class = TaxesForm
    template_name = 'taxes/taxes_form.html'
    success_url = reverse_lazy('taxes-list')

class TaxesUpdateView(UpdateView):
    model = Taxes
    form_class = TaxesForm
    template_name = 'taxes/taxes_form.html'
    success_url = reverse_lazy('taxes-list')

class TaxesDeleteView(DeleteView):
    model = Taxes
    template_name = 'taxes/taxes_confirm_delete.html'
    success_url = reverse_lazy('taxes-list')

# AdditionalCosts Views
class AdditionalCostsListView(ListView):
    model = Additionalcosts
    template_name = 'additionalcosts/additionalcosts_list.html'
    context_object_name = 'additional_costs'

class AdditionalCostsCreateView(FormView):
    form_class = AdditionalCostFormSet
    template_name = 'additionalcosts/additionalcosts_form.html'
    success_url = reverse_lazy('additionalcosts-list')

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
    
    
class AdditionalCostsUpdateView(UpdateView):
    model = Additionalcosts
    form_class = AdditionalCostsForm
    template_name = 'additionalcosts/additionalcosts_form.html'
    success_url = reverse_lazy('additionalcosts-list')

class AdditionalCostsDeleteView(DeleteView):
    model = Additionalcosts
    template_name = 'additionalcosts/additionalcosts_confirm_delete.html'
    success_url = reverse_lazy('additionalcosts-list')



def business_settings(request):
    rates = Rates.objects.first()  # Assuming one rate record exists
    return render(request, "settings/shipping_rates.html", {"rates": rates})

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

    return redirect("business_settings")


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

    return redirect("business_settings")


