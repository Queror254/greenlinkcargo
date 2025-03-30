from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from .models import Rates

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


