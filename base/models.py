from django.db import models
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True 


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




class Product(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = CKEditor5Field()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='products')
    brand = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    rating = models.FloatField(default=0.0)
    num_reviews = models.PositiveIntegerField(default=0)

    featured_image = models.FileField(upload_to='product')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name




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
    terms_conditions = models.TextField(blank=True, null=True)
    privacy_policy = models.TextField(blank=True, null=True)

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

