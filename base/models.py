from django.db import models
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from django.contrib.auth.models import User
from django.db.models import Avg
from decimal import Decimal


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True 


class Attribute(models.Model):
    name = models.CharField(max_length=100)  # Name of the attribute like "Size", "Color", etc.

    def __str__(self):
        return self.name

class AttributeValue(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)  # Link the value to an attribute
    value = models.CharField(max_length=100)  # The actual value of the attribute like "Small", "Medium", "Red"

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"




class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Banner(models.Model):
    image = models.FileField(upload_to='banners')
    alt_text = models.CharField(max_length=100)

    def __str__(self):
        return self.alt_text

class Category(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    thumbnail = models.FileField(upload_to='cats')
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name



class SubCategory(BaseModel):
    parent = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='child')
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Brand(BaseModel):
    name = models.CharField(max_length=50)
    slug = models.SlugField()
    thumbnail = models.FileField(upload_to='brands')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name




class Product(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = CKEditor5Field()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='products')
    brand = models.ForeignKey(Brand, blank=True, null=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)
    rating = models.FloatField(default=0.0)
    num_reviews = models.PositiveIntegerField(default=0)

    attributes = models.ManyToManyField(AttributeValue, related_name="products", blank=True)

    featured_image = models.FileField(upload_to='product')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


    def get_average_rating(self):
        return self.reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    def get_review_count(self):
        return self.reviews.count()

    def update_rating(self):
        avg_rating = self.get_average_rating()
        num_reviews = self.get_review_count()
        self.rating = avg_rating
        self.num_reviews = num_reviews
        self.save()



class SiteInfo(BaseModel):
    site_name = models.CharField(max_length=255, unique=True)
    logo = models.ImageField(upload_to='site_logo/', blank=True, null=True)
    favicon = models.ImageField(upload_to='site_favicon/', blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    facebook_link = models.URLField(blank=True, null=True)
    twitter_link = models.URLField(blank=True, null=True)
    instagram_link = models.URLField(blank=True, null=True)
    youtube_link = models.URLField(blank=True, null=True)

    fb_chat = models.URLField(null=True, blank=True)
    w_chat = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.site_name



class Thumbnail(BaseModel):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='thumbnails')
    image = models.FileField(upload_to='product_thumbnails/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Thumbnail for {self.product.name}"




class FlushSell(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)



class Coupon(BaseModel):
    code = models.CharField(max_length=50, unique=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_spend = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code





class Order(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_orders', null=True, blank=True)
    SHIPPING_CHOICES = [
        ('dhaka', 'Inside Dhaka City'),
        ('chittagong', 'Inside Chittagong City'),
        ('outside', 'Outside Dhaka & Chittagong'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField()
    shipping_method = models.CharField(max_length=20, choices=SHIPPING_CHOICES)
    order_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Order #{self.id} - {self.full_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    size = models.CharField(max_length=50, null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    others = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.subtotal = self.product.discount_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} (x{self.quantity}) - {self.subtotal}"




class Cart(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='carts', null=True,
    blank=True)
    is_paid = models.BooleanField(default=False)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Cart for {self.user.username}"


class CartItems(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0)
    size = models.CharField(max_length=50, null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    other = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


    def total_price(self):

        print(f"Product: {self.product}, Quantity: {self.quantity}, Price: {self.price}")
    
        quantity = Decimal(self.quantity or 0)
        price = Decimal(self.price or 0)
        return quantity * price




class Review(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)], default=5)  # Rating from 1 to 5
    review_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review for {self.product.name} by {self.user.username}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_product_rating()

    def update_product_rating(self):
        product = self.product
        reviews = product.reviews.all()
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        num_reviews = reviews.count()

        product.rating = avg_rating
        product.num_reviews = num_reviews
        product.save()



class ProductAttribute(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_attributes")
    attribute_value = models.ForeignKey(AttributeValue, on_delete=models.CASCADE, related_name="product_values")
    stock = models.PositiveIntegerField(default=0)
    regular_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to="product_attributes/", null=True, blank=True)

    class Meta:
        unique_together = ("product", "attribute_value")  # Ensures unique attributes per product

    def __str__(self):
        return f"{self.product.name} - {self.attribute_value.value}"