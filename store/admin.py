from django.contrib import admin
from .models import Cart, CartItem, Payment, Order, OrderItem, ShippingAddress, Coupon, Offer, Feed, Notification, \
    FlashSale

# Register your models here.


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1


class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 1


class ShippingAddressInline(admin.StackedInline):
    model = ShippingAddress
    extra = 1


class CartAdmin(admin.ModelAdmin):
    inlines = [CartItemInline]
    list_display = ('id', 'user', 'created_at', 'total_quantity', 'calculate_total')


admin.site.register(Cart, CartAdmin)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ('id', 'user', 'created_at', 'shipped', 'is_paid', 'calculate_order_total')


admin.site.register(Order, OrderAdmin)


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'amount', 'payment_method', 'transaction_id', 'payment_status')


admin.site.register(Payment, PaymentAdmin)


class AddressAdmin(admin.ModelAdmin):
    list_display = ('order', 'street', 'city', 'state', 'zip_code')


admin.site.register(ShippingAddress, AddressAdmin)


class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percentage', 'valid_from', 'valid_to', 'is_valid')
    search_fields = ('code',)
    list_filter = ('valid_from', 'valid_to')


admin.site.register(Coupon, CouponAdmin)


class OfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'discount_percentage')
    filter_horizontal = ('products',)


admin.site.register(Offer, OfferAdmin)


class FeedAdmin(admin.ModelAdmin):
    list_display = ('title', 'content', 'created_at')
    search_fields = ('title',)


admin.site.register(Feed, FeedAdmin)


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'content', 'created_at', 'is_read')
    search_fields = ('user__username', 'content')
    list_filter = ('created_at', 'is_read')


admin.site.register(Notification, NotificationAdmin)


class FlashSaleAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'end_time', 'discount_percentage', 'is_active')
    filter_horizontal = ('products',)
    search_fields = ('title',)
    list_filter = ('start_time', 'end_time')


admin.site.register(FlashSale, FlashSaleAdmin)