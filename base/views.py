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






def checkout(request):
    if request.method == 'GET':
        product = Product.objects.get(id=request.GET.get('product_id'))
        quantity = request.GET.get('quantity')

        context = {
            'product' : product,
            'quantity' : quantity
        }
        return render(request, 'checkout.html', context)


    if request.method == "POST":
        full_name = request.POST.get("full_name")
        phone_number = request.POST.get("phone_number")
        email = request.POST.get("email", "")
        address = request.POST.get("address")
        shipping_method = request.POST.get("shipping_method")
        product_id = request.POST.get("product_id")
        discount_amount = float(request.POST.get("total_discount_amount", 0))
        shipping_cost = float(request.POST.get("total_shipping_to_pay", 0))
        total_price = float(request.POST.get("total_price_to_pay", 0))

        order = Order.objects.create(
            full_name=full_name,
            phone_number=phone_number,
            email=email,
            address=address,
            shipping_method=shipping_method,
            discount_amount=discount_amount,
            shipping_cost=shipping_cost,
            total_price=total_price,
        )

        get_product = Product.objects.get(id=product_id)

        oic = OrderItem.objects.create(order=order, product=get_product)





        return JsonResponse({"success": True, "order_id": order.id})

    return render(request, "checkout.html")


def cart(r):
    return render(r, 'cart.html')