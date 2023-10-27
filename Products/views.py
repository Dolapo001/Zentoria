from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Category, SubCategory, Product, FavouriteProduct, Color, Size, ProductReview
from .serializers import (
    CategorySerializer, SubCategorySerializer, ProductSerializer, FavouriteProductSerializer, ColorSerializer,
    SizeSerializer, ProductReviewSerializer
)
# Create your views here.


def custom_response(data, message, status_code, status_text):
    response_data = {
        "status_code": status_code,
        "message": message,
        "data": data,
        "status": status_text,
    }
    return Response(response_data, status=status_code)


class ProductListCategory(APIView):
    @staticmethod
    def get(request, category_id):
        try:
            products = Product.objects.filter(category=category_id)
            serializer = ProductSerializer(products, many=True)
            data = {
                "products": serializer.data
            }
            if not data["products"]:
                return custom_response(data, "No products found", status
                                       .HTTP_404_NOT_FOUND, "error")
            return custom_response(data, "List of Products by Category", status.HTTP_200_OK, "success")
        except Exception as e:
            data = {
                "error_message": f"An error occurred while retrieving products: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")


class ProductListSubCategory(APIView):
    @staticmethod
    def get(request, subcategory_id):
        try:
            products = Product.objects.filter(subcategory=subcategory_id)
            serializer = ProductSerializer(products, many=True)
            data = {
                "products": serializer.data
            }
            if not data["products"]:
                return custom_response(data, "No products found", status
                                       .HTTP_404_NOT_FOUND, "error")
            return custom_response(data, "List of Products by subcategory", status.HTTP_200_OK, "success")
        except Exception as e:
            data = {
                "error_message": f"An error occurred while retrieving products: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")


class CategoryList(APIView):
    @staticmethod
    def get(self, request):
        try:
            categories = Category.objects.all()
            serializer = CategorySerializer(categories, many=True)
            data = {
                "categories": serializer.data
            }
            if not data["categories"]:
                return custom_response(data, "No categories found", status.HTTP_404_NOT_FOUND, "error")
            return custom_response(data, "List of available categories", status.HTTP_200_OK, "success")
        except Exception as e:
            data = {
                "error_message": f"An error occurred while retrieving categories: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")


class SubCategoryList(APIView):
    @staticmethod
    def get(request):
        try:
            subcategories = SubCategory.objects.all()
            serializer = SubCategorySerializer(subcategories, many=True)
            data = {
                "subcategories": serializer.data
            }
            if not data["subcategories"]:
                return custom_response(data, "No subcategories found", status.HTTP_404_NOT_FOUND, "error")
            return custom_response(data, "List of subcategories", status.HTTP_200_OK, "success")
        except Exception as e:
            data = {
                "error_message": f"An error occurred while retrieving subcategories: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")


class ProductDetail(APIView):
    def get(self, request, product_id):
        try:
            product = get_object_or_404(Product, id=product_id)
            serializer = ProductSerializer(product)

            colors = product.available_colors.all()
            sizes = product.available_sizes.all()

            color_serializer = ColorSerializer(colors, many=True)
            size_serializer = SizeSerializer(sizes, many=True)

            product_reviews = product.reviews.all()
            product_review_serializer = ProductReviewSerializer(product_reviews, many=True)

            total_reviews = product_reviews.count()
            if total_reviews > 0:
                total_rating = sum(review.rating for review in product_reviews)
                average_rating = total_rating / total_reviews
            else:
                average_rating = 0

            response_data = {
                "status_code": 200,
                "message": "Product details",
                "data": {
                    "product": serializer.data,
                    "colors": color_serializer.data,
                    "sizes": size_serializer.data,
                    "reviews": product_review_serializer.data,
                    "average_rating": average_rating,
                },
                "status": "success",
            }
            return custom_response(response_data, "Product details retrieved successfully", status.HTTP_200_OK, "success")

        except Exception as e:
            data = {
                "error_message": f"An error occurred while retrieving product details: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")


#class SimilarProductRecommendation(APIView):
