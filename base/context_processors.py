from .models import Category, SiteInfo, Cart, CartItems, Brand
from django.core.cache import cache


def category_context(request):
    categories = Category.objects.prefetch_related('child').all()
    return {'categories': categories}




def site_info_context(request):
    site_info = cache.get('site_info')

    if not site_info:
        site_info = SiteInfo.objects.first()
        cache.set('site_info', site_info, timeout=1000)

    return {'site_info': site_info}




def cart_item_count(request):
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_count = len([item for item in CartItems.objects.filter(cart=cart)])

            print(cart_count)
        except Cart.DoesNotExist:
            cart_count = 0

    return {'cart_count': cart_count}



def get_brands(request):
    brands = Brand.objects.all().order_by('-id')
    return {'all_brands': brands}