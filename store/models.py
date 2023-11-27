from django.db import models
from accounts.models import User
from Products.models import Product


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_total(self):
        total_cost = sum(item.product.price * item.quantity for item in self.cartitem_set.all())
        return round(total_cost, 2)

    def total_quantity(self):
        return sum(item.quantity for item in self.cartitem_set.all())

    def __str__(self):
        return f"Cart {self.id} - User: {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"CartItem {self.id} - Product: {self.product.name}, Quantity: {self.quantity}"


class Payment(models.Model):
    BANK_TRANSFER = 'Bank Transfer'
    CREDIT_DEBIT_CARD = 'Credit/Debit Card'
    FLUTTERWAVE = 'Flutterwave'

    PAYMENT_METHOD_CHOICES = [
        (BANK_TRANSFER, 'Bank Transfer'),
        (CREDIT_DEBIT_CARD, 'Credit/Debit Card'),
        (FLUTTERWAVE, 'Flutterwave'),
    ]

    order = models.OneToOneField('Order', on_delete=models.CASCADE, related_name='payment_relation')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=225,  choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=225)
    payment_status = models.CharField(max_length=50, default='Pending')

    def __str__(self):
        return f"Payment for Order {self.order.id}"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    shipped = models.BooleanField(default=False)
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, null=True, blank=True,
                                   related_name='order_relation')

    def calculate_order_total(self):
        total_cost = sum(item.product.price * item.quantity for item in self.orderitem_set.all())
        return round(total_cost, 2)

    def is_shipped(self):
        return self.shipped

    def is_paid(self):
        return self.payment is not None

    def __str__(self):
        return f"Order {self.id} - User: {self.user.username}, Shipped: {self.shipped}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"OrderItem {self.id} - Product: {self.product.name}, Quantity: {self.quantity}"


class ShippingAddress(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    address = models.TextField()
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Shipping Address'
        verbose_name_plural = 'Shipping Addresses'

    def __str__(self):
        return f"ShippingAddress for Order {self.order.id}"

