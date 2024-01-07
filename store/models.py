from django.db import models
from django.utils import timezone
import secrets
from django.core.exceptions import ValidationError
#from accounts.models import User
#from Products.models import Product


class Cart(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='active')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def calculate_total(self):
        total_cost = sum(item.product.price * item.quantity for item in self.cartitem_set.all())
        return round(total_cost, 2)

    def total_quantity(self):
        return sum(item.quantity for item in self.cartitem_set.all())

    def apply_coupon(self, coupon):
        if not coupon.is_valid():
            raise ValidationError("Cannot apply an invalid coupon.")

        discount_amount = self.calculate_discount(coupon)

        self.total -= discount_amount
        self.save()

    def calculate_discount(self, coupon):
        discount_percentage = coupon.discount_percentage
        total_amount = self.calculate_total()
        discount_amount = (discount_percentage / 100) * total_amount
        return discount_amount

    def __str__(self):
        return f"Cart {self.id} - User: {self.user.username}, Status: {self.status}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey("Products.Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"CartItem {self.id} - Product: {self.product.name}, Quantity: {self.quantity}"


class Order(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    shipped = models.BooleanField(default=False)
    payment = models.OneToOneField('Payment', on_delete=models.CASCADE, null=True, blank=True,
                                   related_name='order_relation')
    status = models.CharField(max_length=20, default='processing')

    def calculate_order_total(self):
        total_cost = sum(item.product.price * item.quantity for item in self.orderitem_set.all())
        return round(total_cost, 2)

    def is_shipped(self):
        return self.shipped

    def is_paid(self):
        return self.payment is not None

    def __str__(self):
        return f"Order {self.id} - User: {self.user.username}, Shipped: {self.shipped}, Status: {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey("Products.Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"OrderItem {self.id} - Product: {self.product.name}, Quantity: {self.quantity}"


class Payment(models.Model):
    BANK_TRANSFER = 'Bank Transfer'
    CREDIT_DEBIT_CARD = 'Credit/Debit Card'
    FLUTTERWAVE = 'Flutterwave'

    PAYMENT_METHOD_CHOICES = [
        (BANK_TRANSFER, 'Bank Transfer'),
        (CREDIT_DEBIT_CARD, 'Credit/Debit Card'),
        (FLUTTERWAVE, 'Flutterwave'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment_relation')
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, default=1)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=225, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=225)
    payment_status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Completed', 'Completed')], default='Pending')

    def __str__(self):
        return f"Payment for Order {self.order.id}"


class ShippingAddress(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    street = models.TextField()
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=10)

    class Meta:
        verbose_name = 'Shipping Address'
        verbose_name_plural = 'Shipping Addresses'

    def __str__(self):
        return f"ShippingAddress for Order {self.order.id}"


class CouponCode(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=8, unique=True, editable=False)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    expired = models.BooleanField(default=False)
    expiry_date = models.DateTimeField()

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = secrets.token_hex(4).upper()

        if self.expiry_date and (timezone.now() > self.expiry_date):
            self.expired = True

        if self.expiry_date < timezone.now():
            raise ValidationError("Expiry date must be in the future")
        super().save(*args, **kwargs)

    def is_valid(self):
        return not self.expired and self.expiry_date > timezone.now()

    def extend_expiry(self, days):
        if self.expiry_date > timezone.now():
            self.expiry_date += timezone.timedelta(days=days)
            self.expired = False
            self.save()

    def deactivate(self):
        self.expired = True
        self.save()






