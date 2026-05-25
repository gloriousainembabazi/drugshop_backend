"""
Main URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('his_grace_drugshop.users.urls')),
    path('api/medicines/', include('his_grace_drugshop.medicines.urls')),
    path('api/sales/', include('his_grace_drugshop.sales.urls')),
    path('api/reports/', include('his_grace_drugshop.reports.urls')),
    path('api/credit/', include('his_grace_drugshop.credit.urls')),           
    path('api/expenses/', include('his_grace_drugshop.expenses.urls')),       
    path('api/prescriptions/', include('his_grace_drugshop.prescriptions.urls')),
    path('api/stock/', include('his_grace_drugshop.stock.urls')),             
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
