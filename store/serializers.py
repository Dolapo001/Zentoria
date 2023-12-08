from rest_framework import serializers
from .models import Order, \
    Cart, OrderItem, \
    CartItem, Payment, \
    ShippingAddress, Coupon, Offer, \
    Feed, Notification, FlashSale
from Products.models import Product
from .validator import validate_quantity, \
    validate_cartitem_set, \
    validate_total_quantity, \
    validate_product, \
    validate_coupon_dates, \
    validate_discount_percentage, \
    validate_flash_sale_dates


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'quantity']

    quantity = serializers.IntegerField(validators=[validate_quantity])
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), validators=[validate_product])


class CartSerializer(serializers.ModelSerializer):
    cartitem_set = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at', 'cartitem_set']

    cartitem_set = serializers.ListField(child=CartItemSerializer(validators=[validate_cartitem_set]))
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


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = ['id', 'user', 'order', 'street', 'city', 'state', 'zip_code']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'user', 'order', 'amount', 'payment_method']


class FeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feed
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'

    def validate(self, data):
        validate_coupon_dates(data.get('valid_from'), data.get('valid_to'))
        return data


class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = '__all__'

    def validate_discount_percentage(self, value):
        return validate_discount_percentage(value)


class FlashSaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlashSale
        fields = '__all__'

    def validate(self, data):
        validate_flash_sale_dates(data.get('start_time'), data.get('end_time'))
        return data