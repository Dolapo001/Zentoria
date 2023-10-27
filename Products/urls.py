from django.urls import path
from .views import ProductListCategory, ProductListSubCategory, CategoryList, SubCategoryList, ProductDetail

urlpatterns = [
    path('categories/', CategoryList.as_view(), name='category-list'),
    path('products/<uuid:product_id>', ProductDetail.as_view(), name='product-detail'),
    path('subcategories/', SubCategoryList.as_view(), name='subcategory-list'),
    path('category/<int:category_id>/', ProductListCategory.as_view(), name='product-list-category'),
    path('subcategory/<int:subcategory_id>/', ProductListSubCategory.as_view(), name='product-list-subcategory'),
]
