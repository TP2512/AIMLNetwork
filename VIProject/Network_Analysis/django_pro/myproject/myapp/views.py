# myapp/views.py
from django.http import JsonResponse
from django.shortcuts import render

from .forms import CircleForm, VendorForm
from .models import Circle, Vendor


def cascading_dropdowns(request):
    circles = Circle.objects.all()
    return render(request, 'cascading_dropdowns.html',
                  {'circles': circles, 'circle_form': CircleForm(), 'vendor_form': VendorForm()})


def get_vendors(request):
    circle_id = request.GET.get('circle_id')
    vendors = Vendor.objects.filter(circle_id=circle_id).values('id', 'name')
    return JsonResponse(list(vendors), safe=False)
