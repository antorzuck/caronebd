from django.shortcuts import render, redirect, get_object_or_404
from base.models import *
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt



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




def cart(request):

    try:
        cart = Cart.objects.get(user=request.user)
    except:
        return render(request, 'empty.html')

    cart_items = cart.cart_items.all()

    if len(cart_items) == 0:
        return render(request, 'empty.html')
    total_price = sum(item.total_price() for item in cart_items)
 

    if request.method == 'POST':
        code = request.POST.get('code')
        coupon = Coupon.objects.filter(code=code)

        if cart.coupon:
            messages.error(request, "A coupon already exists on this cart.")
            return redirect('/cart')

        if coupon.exists():
            if coupon[0].is_active:
                if total_price >= coupon[0].minimum_spend:
                    cart.coupon = coupon[0]
                    cart.save()
                else:
                    messages.error(request, f"Minimum amount should be {coupon[0].minimum_spend} or more to use this coupon")
                    return redirect('/cart')
                return redirect("/cart")
            messages.error(request, "You late bro! this coupon has expired")
        messages.error(request, "This coupon? never heard of that!")

    context = {
    'cart': cart, 
    'cart_items': cart_items,
    'subtotal' : total_price,
    'total_price_to_pay' : total_price
    
    }

    if cart.coupon:
        if total_price < cart.coupon.minimum_spend:
            messages.info(request, "Dont try to be smart. coupon got removed!")
            cart.coupon = None
            cart.save()
            return redirect('/cart')
        
        total_price_to_pay = total_price - cart.coupon.discount_amount

        context['total_price_to_pay'] = total_price_to_pay
        context['coupon_discount'] = cart.coupon.discount_amount


    
    return render(request, 'cart.html', context)




def add_to_cart(request):
    product_id = request.GET.get('product_id')
    quantity = request.GET.get('quantity', 1)
    
    if not product_id:
        return JsonResponse({'error': 'Product ID is required'}, status=400)
    
    product = get_object_or_404(Product, id=product_id)
    
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User must be logged in'}, status=401)

    try:
        cart = Cart.objects.get(user=request.user, is_paid=False)
    except :
        cart = Cart.objects.create(user=request.user)
    
    cart_item, item_created = CartItems.objects.get_or_create(cart=cart, product=product)
    cart_item.quantity += int(quantity)
    cart_item.save()
    
    return redirect('/cart')




@csrf_exempt
def update_cart_item(request, item_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        quantity = data.get('quantity')

        # Fetch the cart item and update its quantity
        cart_item = get_object_or_404(CartItem, id=item_id)
        cart_item.quantity = quantity
        cart_item.save()

        # Recalculate the total price
        cart = cart_item.cart
        cart_total = sum(item.product.price * item.quantity for item in cart.cart_items.all())
        cart.total_price = cart_total
        cart.save()

        return JsonResponse({'success': True, 'new_total_price': cart_total})



def increase_quantity(request, product_id):
    cart = Cart.objects.get(user=request.user, is_paid=False)
    cart_item = CartItems.objects.get(cart=cart, id=product_id)

    cart_item.quantity += 1
    cart_item.save()

    return redirect('/cart')


def decrease_quantity(request, product_id):
    cart = get_object_or_404(Cart, user=request.user, is_paid=False)
    cart_item = get_object_or_404(CartItems, cart=cart, id=product_id)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()

    return redirect('/cart')


def remove_item(request, product_id):
    cart = get_object_or_404(Cart, user=request.user, is_paid=False)
    cart_item = CartItems.objects.filter(cart=cart, id=product_id).first()

    if cart_item:
        cart_item.delete()

    return redirect('/cart')
