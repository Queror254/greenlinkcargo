from django import forms
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
        fields = ['name', 'value']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'value': forms.NumberInput(attrs={'class': 'form-control'}),
        }