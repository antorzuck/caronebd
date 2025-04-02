from django.shortcuts import render, redirect, get_object_or_404
from base.models import *
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout, authenticate
from django.db.models import Q
from urllib.parse import unquote
from collections import defaultdict
from django.core.paginator import Paginator
from django.core.files.base import ContentFile
from django.utils.text import slugify
import base64
from rest_framework.decorators import api_view
from rest_framework.response import Response
from decimal import Decimal
from django.db.models import Count


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

    products = Product.objects.filter(is_active=True).order_by('?')[:15]

    brands = Brand.objects.all().order_by('?')[:15]

    context = {
        'banners' : banners,
        'products' : products,
        'flashs' : flash,
        'brands' : brands
    }
    return render(r, 'home.html', context)




def product_view(r, slug):
    try:
        get_product = Product.objects.get(slug=slug)
        rvw = Review.objects.filter(product=get_product)


        grouped_attributes = defaultdict(list)
        for attribute in get_product.attributes.all():
            grouped_attributes[attribute.attribute.name].append(attribute.value)

        # Count total reviews
        total_reviews = rvw.count()

        # Get count of each rating
        rating_counts = rvw.values('rating').annotate(count=Count('rating'))

        # Calculate percentages (as whole numbers)
        rating_percentages = {
            item['rating']: (item['count'] * 100) // total_reviews  # Integer division
            for item in rating_counts
        } if total_reviews > 0 else {}

        list_of_price = []
        if get_product.discount_price == 0 or get_product.discount_price == None:
            pa = filtered_attributes = ProductAttribute.objects.filter(
    product=get_product)

            print(pa)

            f_obj = pa.first()
            l_obj = pa.last()

            if f_obj:
                if not f_obj.sale_price == None:
                    list_of_price.append(f_obj.sale_price)
                else:
                    list_of_price.append(f_obj.regular_price)

            if l_obj:
                if not l_obj.sale_price == None:
                    list_of_price.append(l_obj.sale_price)
                else:
                    list_of_price.append(l_obj.regular_price)
            
        print(list_of_price)
        print("MSKI CHUUT THR LIST OF PRICEEEE")


        context = {
            'product': get_product,
            'rvw': rvw,
            'rating_percentages': rating_percentages,
            'grouped_attributes': dict(grouped_attributes),
            'alter_price' : "-".join(str(int(value)) for value in list_of_price if value is not None)
        }
        
    except Exception as e:
        print(e)
        return redirect('/')
    
    return render(r, 'product-view.html', context)




def checkout(request):
    if request.method == 'GET':
        product = Product.objects.get(id=request.GET.get('product_id'))
        quantity = request.GET.get('quantity')

        params = request.GET
        param_string = "\n".join([
            f"{key}={','.join(value)}"
            for key, value in params.lists()
            if not (key.startswith("product_id") or key.startswith("hm_price") or key.startswith("quantity"))])

        size = request.GET.get('size')
        color = request.GET.get('color')
        other = param_string

        context = {
            'product' : product,
            'quantity' : quantity,
            'size' : size,
            'color' : color,
            'other' : other
        }
        return render(request, 'checkout.html', context)


    if request.method == "POST":
 
        full_name = request.POST.get("full_name")
        phone_number = request.POST.get("phone_number")
        email = request.POST.get("email", "")
        address = request.POST.get("address")
        shipping_method = request.POST.get("shipping_method")
        product_id = request.POST.get("product_id")
        cart_id = request.POST.get("cart_id")
        try:
            discount_amount = float(request.POST.get("total_discount_amount", 0))
        except:
            discount_amount = 0
        shipping_cost = float(request.POST.get("total_shipping_to_pay", 0))
        total_price = float(request.POST.get("total_price_to_pay", 0))


        quantity = request.POST.get('quantity')
        size = request.POST.get('size')
        color = request.POST.get('color')
        other = request.POST.get('other')


        order = Order.objects.create(
            user=request.user,
            full_name=full_name,
            phone_number=phone_number,
            email=email,
            address=address,
            shipping_method=shipping_method,
            discount_amount=discount_amount,
            shipping_cost=shipping_cost,
            total_price=total_price,
        )

        if cart_id:
            get_cart = Cart.objects.get(id=cart_id)
            products = CartItems.objects.filter(cart=get_cart)

            for p in products:
                OrderItem.objects.create(order=order, product=p.product, quantity=p.quantity, size=p.size,
                color=p.color, others=p.other)
            
            get_cart.delete()

        if product_id:
            get_product = Product.objects.get(id=product_id)
            oic = OrderItem.objects.create(order=order, product=get_product, quantity=int(quantity), size=size, color=color, others=other)

        return redirect('/orders')
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

    params = request.GET
    param_string = "\n".join([
    f"{key}={','.join(value)}"
    for key, value in params.lists()
    if not (key.startswith("product_id") or key.startswith("hm_price") or key.startswith("quantity"))])

    product_id = request.GET.get('product_id')
    quantity = request.GET.get('quantity', 1)

    size = request.GET.get('size')
    color = request.GET.get('color')
    other = param_string

    price = request.GET.get('hm_price')
    
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
    cart_item.size = size
    cart_item.price = price
    cart_item.color = color
    cart_item.other = other
    cart_item.save()
    
    return redirect('/cart')





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

    if len(CartItems.objects.filter(cart=cart)) == 0:
        cart.delete()

    return redirect('/cart')



def orders(request):
    orders = Order.objects.filter(user=request.user).prefetch_related("items__product").order_by('-id')
    
    context = {
        "orders": orders,
    }
    return render(request, "orders.html", context)






def register(request):
    if request.method == 'POST':
    
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone').strip()
        address = request.POST.get('address')
        password = request.POST.get('password').strip()
        slug = request.POST.get('slug')

        if User.objects.filter(username=phone).exists():
            messages.error(request, "A user with this phone number already exists.")
            return redirect(f'/product/{slug}')

        
        user = User.objects.create_user(username=phone, password=password, first_name=full_name)
        user.save()

    
        Profile.objects.create(user=user, phone=phone, address=address, name=full_name)

    
        login(request, user)
        messages.success(request, "Registration successfull.")
        if not slug:
            return redirect('/profile')
        return redirect(f'/product/{slug}')

    return render(request, 'register.html')




def category_view(request, slug):
  
    category = get_object_or_404(Category, slug=slug)

    subcats = category.child.all()

    sort_by = request.GET.get('sort', '-id')
    brands = request.GET.get('brands')
    price = request.GET.get('price')

   
    products = Product.objects.filter(category__in=subcats, is_active=True)

 
    if brands:
        brand_list = unquote(brands).split(',')
        products = products.filter(brand__in=brand_list)

    if price:
        products = products.filter(price__lte=price)

   
    if sort_by == '-id':
        products = products.order_by('-id')

    if sort_by == 'price-low':
        products = products.order_by('discount_price')
    
    if sort_by == 'price-high':
        products = products.order_by('-discount_price')


    
    context = {
        'products' : products,
        'category' : category
    }

    
    return render(request, 'category.html', context)





def brand_view(request, slug):
  
    the_brand = get_object_or_404(Brand, slug=slug)

    sort_by = request.GET.get('sort', '-id')
    brands = request.GET.get('brands')
    price = request.GET.get('price')

   
    products = Product.objects.filter(brand=the_brand, is_active=True)

 
    if brands:
        brand_list = unquote(brands).split(',')
        products = products.filter(brand__in=brand_list)

    if price:
        products = products.filter(price__lte=price)

   
    if sort_by == '-id':
        products = products.order_by('-id')

    if sort_by == 'price-low':
        products = products.order_by('discount_price')
    
    if sort_by == 'price-high':
        products = products.order_by('-discount_price')


    
    context = {
        'products' : products,
        'category' : the_brand
    }

    
    return render(request, 'category.html', context)




def search_view(request):

    q = request.GET.get('q')
  
    sort_by = request.GET.get('sort', '-id')
    brands = request.GET.get('brands')
    price = request.GET.get('price')

   
    products = Product.objects.filter(name__icontains=q, is_active=True)

 
    if brands:
        brand_list = unquote(brands).split(',')
        products = products.filter(brand__in=brand_list)

    if price:
        products = products.filter(price__lte=price)

   
    if sort_by == '-id':
        products = products.order_by('-id')

    if sort_by == 'price-low':
        products = products.order_by('discount_price')
    
    if sort_by == 'price-high':
        products = products.order_by('-discount_price')


    
    context = {
        'products' : products,
        'q' : q
    }

    
    return render(request, 'category.html', context)












def sub_category_view(request, slug):
  
    category = get_object_or_404(SubCategory, slug=slug)

    sort_by = request.GET.get('sort', '-id')
    brands = request.GET.get('brands')
    price = request.GET.get('price')

   
    products = Product.objects.filter(category=category, is_active=True)

    print(products)
    print(sort_by)
    print(brands)

    if brands:
        brand_list = unquote(brands).split(',')
        products = products.filter(brand__in=brand_list)

    if price:
        products = products.filter(price__lte=price)

   
    if sort_by == '-id':
        products = products.order_by('-id')

    if sort_by == 'price-low':
        products = products.order_by('discount_price')
    
    if sort_by == 'price-high':
        products = products.order_by('-discount_price')


    
    context = {
        'products' : products,
        'category' : category
    }

    
    return render(request, 'category.html', context)


def profile(r):

    if not r.user.is_authenticated:
        return render(r, 'register.html')
    orders = Order.objects.filter(user=r.user).count()

    rvs = Review.objects.filter(user=r.user).order_by('-id')

    rvws = rvs.count()

    context = {
        'orders' : orders,
        'rvws' : rvws,
        'rvs' : rvs
    }
    return render(r, 'profile.html', context)



def logged_out(request):
    logout(request)
    messages.error(request, "logged out.")
    return redirect('/')

def login_handle(request):
    if request.method == 'POST':
        username = request.POST.get('phone')
        password = request.POST.get('password')


        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/profile')
        else:
            messages.error(request, "Credentials not valid.")
            return render(request, 'login.html')

        


    return render(request, 'login.html')






def order_list(request):

    if not request.user.is_staff:
        messages.error(request, "Only admin can view this page.")
        return redirect('/')
    status_filter = request.GET.get('status', 'all')
    
    if status_filter == "all":
        orders = Order.objects.all().order_by('-id')
    else:
        orders = Order.objects.filter(order_status=status_filter).order_by('-id')

    
    paginator = Paginator(orders, 10)  
    page_number = request.GET.get('page')  
    page_obj = paginator.get_page(page_number)

    context = {
        "orders": page_obj,
        "status_filter": status_filter,
    }
    return render(request, "orders/order_list.html", context)


def order_detail(request, order_id):
    if not request.user.is_staff:
        messages.error(request, "Only admin can view this page.")
        return redirect('/')
    order = get_object_or_404(Order, id=order_id)
    context = {"order": order}
    return render(request, "orders/order_detail.html", context)


def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == "POST":

        if not request.user.is_staff:
            messages.error(request, "Only admin can view this page.")
            return redirect('/')
        new_status = request.POST.get("order_status")
        order.order_status = new_status
        order.save()
        messages.success(request, "Order status updated successfully!")
        return redirect(f'/orders/{order_id}')



def get_attributes(request):
    id = request.GET.get('id')
    product = request.GET.get('product')

    attrval = AttributeValue.objects.get(value=id)
    product = Product.objects.get(id=product)

    try:
        xxx = ProductAttribute.objects.get(
            product=product,
            attribute_value=attrval
        )
    except ProductAttribute.DoesNotExist:
        return JsonResponse({"have_price": False})

    if xxx.sale_price is not None and xxx.sale_price > 0:
        return JsonResponse({
            "have_price": True,
            "price": xxx.sale_price,
            "image": xxx.image.url
        })
    elif xxx.regular_price is not None and xxx.regular_price > 0:
        return JsonResponse({
            "have_price": True,
            "price": xxx.regular_price,
            "image": xxx.image.url
        })
    else:
        return JsonResponse({"have_price": False, "price": "0"})


def create_pro(r):
    return render(r, 'createpro.html')


@api_view(['POST'])
def create_product(request):
    data = request.data


    try:
        # Fetching category and brand
        category = SubCategory.objects.get(name=data['category'])
        try:
            brand = Brand.objects.get(name=data['brand'])
        except:
            brand = None

        # Creating the Product
        product = Product.objects.create(
            name=data['title'],
            slug=slugify(data['slug']),
            description=data['description'],
            price=data['regular_price'],
            discount_price=data['sale_price'],
            stock=data['stock_qty'],
            category=category,
            brand=brand,
            is_active=True,
            featured_image=save_base64_image(data['main_image'], 'product_main')
        )

        # Save gallery images
        gallery_images = data.getlist('gallery_images[]')
        for index, img in enumerate(gallery_images):
            print(f"Saving Gallery Image {index}: {img}")
            Thumbnail.objects.create(
                product=product,
                image=save_base64_image(img, f'product_thumbnail_{index}')
            )

        # Saving Variations (Attributes like capacity and color)
        variation_attributes = data.getlist('variation_attributes[]')
        for attr in variation_attributes:
            print("Processing attribute:", attr)

            try:
                # Ensure the attribute is in the 'attribute:value' format
                if ':' not in attr:
                    raise ValueError(f"Invalid format for variation attribute: {attr}")

                attr_type, attr_value = attr.split(':')
                print(f"Processing attribute: {attr_type} - {attr_value}")

             
                attribute = Attribute.objects.get(name=attr_type)

             
                attribute_value = AttributeValue.objects.filter(attribute=attribute, value=attr_value).first()

               
                product.attributes.add(attribute_value)

            except Attribute.DoesNotExist:
                print(f"Error: Attribute '{attr_type}' does not exist.")
                continue  # Skip this attribute if it doesn't exist

            except Exception as e:
                print(f"Error processing attribute {attr}: {e}")
                continue  # Skip this attribute if there's an error

            # Ensure key formatting matches the QueryDict keys
            key_stock = f'variation_stock_{attribute.name}_{attr_value.lower().replace(" ", "_")}'
            key_regular_price = f'variation_regular_price_{attribute.name}_{attr_value.lower().replace(" ", "_")}'
            key_sale_price = f'variation_sale_price_{attribute.name}_{attr_value.lower().replace(" ", "_")}'
            key_image = f'variation_image_{attribute.name}_{attr_value.lower().replace(" ", "_")}'

            # Extract values correctly
            stock = int(data.getlist(key_stock)[0]) if key_stock in data else 0
            regular_price = Decimal(data.getlist(key_regular_price)[0]) if key_regular_price in data else Decimal(0)
            sale_price = Decimal(data.getlist(key_sale_price)[0]) if key_sale_price in data else Decimal(0)
            image = request.FILES.get(key_image)

            print(f"Stock: {stock}, Regular Price: {regular_price}, Sale Price: {sale_price}, Image: {image}")
            # ✅ Now creating Product Attribute correctly
            ProductAttribute.objects.create(
                product=product,
                attribute_value=attribute_value,
                stock=stock,
                regular_price=regular_price,
                sale_price=sale_price if sale_price else None,
                image=image
            )

        return Response({"message": "Product created successfully!", "product_id": product.id})

    except Exception as e:
        print("Error in creating product:", e)
        return Response({"error": str(e)}, status=400)



def save_base64_image(data, filename):
    if data.startswith('data:image'):
        format, imgstr = data.split(';base64,')
        ext = format.split('/')[-1]
        return ContentFile(base64.b64decode(imgstr), name=f'{filename}.{ext}')
    return None



def fetch_categories(request):
    if request.method == 'GET':
        categories = SubCategory.objects.values('name')
        category_list = list(categories)
        return JsonResponse(category_list, safe=False)

def fetch_brand(request):
    if request.method == 'GET':
        brands = Brand.objects.values('name')  
        brand_list = list(brands)
        return JsonResponse(brand_list, safe=False)

def fetch_attributes(request):
    if request.method == 'GET':
        attributes = Attribute.objects.all()
        attribute_list = []
        
        for attribute in attributes:
            values = list(AttributeValue.objects.filter(attribute=attribute).values_list('value', flat=True))
            attribute_list.append({
                'value': attribute.name,  
                'name': attribute.name,
                'values': values
            })
        
        return JsonResponse(attribute_list, safe=False)
