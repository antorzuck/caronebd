from django.contrib import admin
from .models import *

admin.site.register(Profile)
admin.site.register(Brand)
admin.site.register(Banner)
admin.site.register(FlushSell)
admin.site.register(OrderItem)

admin.site.register(Cart)
admin.site.register(CartItems)
admin.site.register(Review)
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'phone_number', 'shipping_method', 'total_price')
    search_fields = ('full_name', 'phone_number', 'email')
    list_filter = ('shipping_method', 'created_at')
    ordering = ('-created_at',)


class ThumbnailInline(admin.TabularInline):  # Inline admin for thumbnails
    model = Thumbnail
    extra = 1

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_amount', 'is_active')
    search_fields = ('code',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'thumbnail')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    list_filter = ('created_at',)


@admin.register(SubCategory)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    list_filter = ('created_at',)



@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price')
    search_fields = ('name', 'category__name', 'brand')
    list_filter = ('category', 'is_active', 'created_at')
    date_hierarchy = 'created_at'
    inlines = [ThumbnailInline]

@admin.register(SiteInfo)
class SiteInfoAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'contact_email', 'contact_phone', 'updated_at')
    search_fields = ('site_name', 'contact_email')
    readonly_fields = ('created_at', 'updated_at')

