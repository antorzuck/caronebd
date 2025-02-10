from django.shortcuts import render, redirect
from base.models import *




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