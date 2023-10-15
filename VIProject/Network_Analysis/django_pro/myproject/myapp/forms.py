# myapp/forms.py
from django import forms
from .models import Circle, Vendor

class CircleForm(forms.ModelForm):
    class Meta:
        model = Circle
        fields = ['name']

class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['name', 'circle']
