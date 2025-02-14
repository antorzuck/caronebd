from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from base.views import *



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),
    path('product/<str:slug>', product_view),
    path('checkout', checkout),
    path('api/check-coupon/', check_coupon, name='check-coupon'),
    path('cart', cart),
    path('add-to-cart', add_to_cart),
    path("ckeditor5/", include('django_ckeditor_5.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
