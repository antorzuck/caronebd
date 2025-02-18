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
    path('cart/increase/<int:product_id>/', increase_quantity),
    path('cart/decrease/<int:product_id>/', decrease_quantity),
    path('cart/remove/<int:product_id>/', remove_item),
    path('orders/', orders),
    path('register', register),
    path('category/<str:slug>', category_view),
    path('subcategory/<str:slug>', sub_category_view),
    path('profile', profile),
    path("ckeditor5/", include('django_ckeditor_5.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
