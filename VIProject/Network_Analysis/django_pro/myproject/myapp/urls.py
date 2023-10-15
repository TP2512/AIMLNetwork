# myapp/urls.py
from django.urls import path
from .views import cascading_dropdowns, get_vendors

urlpatterns = [
    path('cascading-dropdowns/', cascading_dropdowns, name='cascading_dropdowns'),
    path('get_vendors/', get_vendors, name='get_vendors'),
]
