from django.contrib import admin
from .models import Category, Style, Product, ProductReview, SubCategory, Size, Color


# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    list_filter = ['parent_category']
    search_fields = ['name']


class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent_category']
    list_filter = ['parent_category']
    search_fields = ['name']


class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'quantity', 'category']
    list_filter = ['subcategory__name']
    search_fields = ['name', 'description']


class StyleAdmin(admin.ModelAdmin):
    list_display = ['style']


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['name']


admin.site.register(Product, ProductAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(ProductReview)
admin.site.register(Style, StyleAdmin)

