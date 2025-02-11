from django.shortcuts import render, redirect
from base.models import *
from django.http import JsonResponse



def check_coupon(request):
    code = request.GET.get('code', '').strip().lower()

    try:
        coupon = Coupon.objects.get(code__iexact=code, is_active=True)
        return JsonResponse({"valid": True, "discount": float(coupon.discount_amount)})
    except Coupon.DoesNotExist:
        return JsonResponse({"valid": False, "discount": 0})



def home(r):
    banners = Banner.objects.all().order_by('-id')

    flash = FlushSell.objects.all().order_by('?')[:10]

    products = Product.objects.filter(is_active=True).order_by('-id')[:15]

    context = {
        'banners' : banners,
        'products' : products,
        'flashs' : flash
    }
    return render(r, 'home.html', context)


def product_view(r, slug):
    try:
        get_product = Product.objects.get(slug=slug)

        context = {
            'product' : get_product
        }
    except:
        return redirect('/')
    return render(r, 'product-view.html', context)




def checkout(r):
    if r.method == 'GET':
        product = Product.objects.get(id=r.GET.get('product_id'))
        context = {
            'product' : product
        }
        return render(r, 'checkout.html', context)