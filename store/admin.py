from django.contrib import admin
from .models import Cart, CartItem, Payment, Order, OrderItem, ShippingAddress


# Register your models here.

class CartItemInline(admin.TabularInline):
    model = CartItem
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
    list_display = ('order', 'address', 'city', 'state')


admin.site.register(ShippingAddress, AddressAdmin)

