from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets
from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Rates, Taxes, Additionalcosts
from .serializers import TaxesSerializer, AdditionalcostsSerializer
from .forms import TaxesForm, AdditionalCostsForm


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

class AdditionalCostsCreateView(CreateView):
    model = Additionalcosts
    form_class = AdditionalCostsForm
    template_name = 'additionalcosts/additionalcosts_form.html'
    success_url = reverse_lazy('additionalcosts-list')

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
    return render(request, "dash/settings.html", {"rates": rates})

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


