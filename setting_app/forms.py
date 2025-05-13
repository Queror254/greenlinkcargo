from django import forms
from django.forms import formset_factory
from .models import Taxes, Additionalcosts

class TaxesForm(forms.ModelForm):
    class Meta:
        model = Taxes
        fields = ['name', 'rate']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'rate': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class AdditionalCostsForm(forms.ModelForm):
    class Meta:
        model = Additionalcosts
        fields = ['name', 'value']  # shipment is handled separately
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'value': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        # Remove 'shipment' from kwargs before calling parent's __init__
        self.shipment = kwargs.pop('shipment', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.shipment:
            instance.shipment = self.shipment
        if commit:
            instance.save()
        return instance 
    
# Create the formset after the form class is defined
AdditionalCostFormSet = formset_factory(
    AdditionalCostsForm,  # Note: Changed to match the class name
    extra=1,
    can_delete=True
)