from django.db import models
from django.utils import timezone

from accounts.models import User
from Products.models import Product


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='active')

    def calculate_total(self):
        total_cost = sum(item.product.price * item.quantity for item in self.cartitem_set.all())
        return round(total_cost, 2)

    def total_quantity(self):
        return sum(item.quantity for item in self.cartitem_set.all())

    def __str__(self):
        return f"Cart {self.id} - User: {self.user.username}, Status: {self.status}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"CartItem {self.id} - Product: {self.product.name}, Quantity: {self.quantity}"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
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
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
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
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)  # Update this line with an appropriate default user ID
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


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()

    def is_valid(self):
        now = timezone.now()
        return self.valid_from <= now <= self.valid_to

    def __str__(self):
        return f"Coupon {self.code}"


class Offer(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    products = models.ManyToManyField(Product)

    def __str__(self):
        return self.title


class Feed(models.Model):
    title = models.CharField(max_length=225)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username}"


class FlashSale(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    products = models.ManyToManyField(Product)

    def is_active(self):
        now = timezone.now()
        return self.start_time <= now <= self.end_time

    def __str__(self):
        return self.title




