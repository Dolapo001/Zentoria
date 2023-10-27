from django.db import models
from django.contrib.auth.models import User
import random
import string
import uuid


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    icon = models.ImageField(upload_to='category_icons/', null=True, blank=True)
    parent_category = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name='subcategories_of')
    description = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Style(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    style = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.style


class SubCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    parent_category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')

    class Meta:
        verbose_name = "Subcategory"
        verbose_name_plural = "Subcategories"

    def __str__(self):
        return self.name


class Size(models.Model):
    SIZE_CHOICES = [
        ('X', 'X'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('XXL', 'XXL'),
        ('3XL', '3XL'),
    ]

    name = models.CharField(max_length=50, choices=SIZE_CHOICES, unique=True)

    def __str__(self):
        return self.name


class Color(models.Model):
    COLOR_CHOICES = [
        ('blue', 'Blue'),
        ('black', 'Black'),
        ('white', 'White'),
        ('yellow', 'Yellow'),
        ('green', 'Green'),
        ('red', 'Red'),
    ]

    name = models.CharField(max_length=50, choices=COLOR_CHOICES, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='products')
    image = models.ImageField(upload_to='product_images/')
    specification = models.CharField(max_length=100, blank=True, null=True)
    style = models.ForeignKey(Style, on_delete=models.SET_NULL, null=True)
    style_code = models.CharField(max_length=10, blank=True, null=True, unique=True)
    available_sizes = models.ManyToManyField(Size)
    available_colors = models.ManyToManyField(Color)

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.style_code:
            code_length = 10
            alphanumeric_characters = string.ascii_letters + string.digits
            self.style_code = ''.join(random.choice(alphanumeric_characters) for _ in range(code_length))
        super().save(*args, **kwargs)


class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    review_text = models.TextField()
    review_date = models.DateTimeField(auto_now_add=True)
    review_image = models.ImageField(upload_to='review_images/', null=True, blank=True)

    def __str__(self):
        return f"Review for {self.product.name} by {self.user.username}"


class FavouriteProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorites')
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Favourite: {self.product.name}"
