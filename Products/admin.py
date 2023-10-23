from django.contrib import admin
from .models import Category, Style, Product, ProductAttribute, ProductReview, SubCategory



# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent_category', 'description']
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


admin.site.register(Product, ProductAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(ProductAttribute)
admin.site.register(ProductReview)
admin.site.register(Style, StyleAdmin)
