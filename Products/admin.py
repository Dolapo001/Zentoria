from django.contrib import admin
from .models import Category, Product, ProductAttribute, ProductReview


# Register your models here.
class SubcategoryInline(admin.TabularInline):
    model = Category
    fk_name = 'category'
    extra = 1


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    list_filter = ['category']
    search_fields = ['name']
    inlines = [SubcategoryInline]


class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'inventory', 'category']
    list_filter = ['category']
    search_fields = ['name', 'description']


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(ProductAttribute)
admin.site.register(ProductReview)
