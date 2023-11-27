from rest_framework import serializers
from .models import Order, Cart, OrderItem, CartItem, Payment, ShippingAddress
from Products.models import Product
from .validator import validate_quantity, validate_cart_item_set, validate_total_quantity, validate_product


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'quantity']

    quantity = serializers.IntegerField(validators=[validate_quantity])
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), validators=[validate_product])


class CartSerializer(serializers.ModelSerializer):
    cart_item_set = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at', 'cartitem_set']

    cart_item_set = serializers.ListField(child=CartItemSerializer(validators=[validate_cart_item_set]))
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate_cartitem_set(self, value):
        return validate_total_quantity(value)


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', 'created_at', 'shipped', 'payment']


class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['user']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'quantity']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'order', 'amount', 'payment_method', 'transaction_id', 'payment_status']


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = ['id', 'order', 'address', 'city', 'state']
