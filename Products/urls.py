from django.urls import path
from .views import ProductListCategory, ProductListSubCategory, CategoryList, SubCategoryList, ProductDetail, SimilarProductRecommendation, FavouriteProductList, FavouriteProductDetail, ProductSearch

urlpatterns = [
    path('categories/', CategoryList.as_view(), name='category-list'),
    path('products/<uuid:product_id>', ProductDetail.as_view(), name='product-detail'),
    path('subcategories/', SubCategoryList.as_view(), name='subcategory-list'),
    path('category/<int:category_id>/', ProductListCategory.as_view(), name='product-list-category'),
    path('subcategory/<int:subcategory_id>/', ProductListSubCategory.as_view(), name='product-list-subcategory'),
    path('similar-products/<uuid:product_id>/', SimilarProductRecommendation.as_view(), name='similar-products'),
    path('products/search/', ProductSearch.as_view(), name='product-search'),
    path('favorite-products/', FavouriteProductList.as_view(), name='favorite-product-list'),
    path('favorite-products/<int:favorite_product_id>/', FavouriteProductDetail.as_view(), name='favorite-product-detail'),
]
