from rest_framework import serializers
from .models import Taxes, Additionalcosts

class TaxesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Taxes
        fields = '__all__'

class AdditionalcostsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Additionalcosts
        fields = '__all__'
