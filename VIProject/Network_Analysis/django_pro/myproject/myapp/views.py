# myapp/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Circle, Vendor
from .forms import CircleForm,VendorForm
def cascading_dropdowns(request):
    circles = Circle.objects.all()
    return render(request, 'cascading_dropdowns.html', {'circles': circles, 'circle_form': CircleForm(), 'vendor_form': VendorForm()})

def get_vendors(request):
    circle_id = request.GET.get('circle_id')
    vendors = Vendor.objects.filter(circle_id=circle_id).values('id', 'name')
    return JsonResponse(list(vendors), safe=False)
