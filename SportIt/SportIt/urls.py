"""
URL configuration for SportIt project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from core import views
from . import settings
from bookings.views import payment_cancel, payment_success

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_page, name='home'),
    path('users/', include('users.urls')),
    path('venues/', include('venues.urls')),
    path('bookings/', include('bookings.urls')),
    path('payment/cancel/', payment_cancel, name='payment_cancel'),
    path('payment/success/', payment_success, name='payment_success'),

] + static (settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
