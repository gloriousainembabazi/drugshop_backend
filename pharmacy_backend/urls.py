"""
Main URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

# ✅ ADD SIMPLE HOME ENDPOINT (fixes 404 on "/")
def home(request):
    return JsonResponse({
        "message": "Drugshop Backend is running 🚀"
    })

urlpatterns = [
    path('', home),  # ✅ FIX: root URL now works

    path('admin/', admin.site.urls),
    path('api/auth/', include('his_grace_drugshop.users.urls')),

    # 🌟 FIXED: Added this route line to capture user profile/language startup requests
    path('api/user/', include('his_grace_drugshop.users.urls')),

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