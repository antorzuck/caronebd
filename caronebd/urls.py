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
    path('logout/', logged_out),
    path('login', login_handle),
    path('get-attributes/', get_attributes),
    path('orders-manage/', order_list, name="order_list"),
    path('create-product/', create_product),
    path('create-pro', create_pro),
    path('orders/<int:order_id>/', order_detail, name="order_detail"),
    path('update-order/<int:order_id>/', update_order_status, name="update_order_status"),
    path("ckeditor5/", include('django_ckeditor_5.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
