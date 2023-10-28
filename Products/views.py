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
    def get(self, request, category_id):
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
    def get(self, request, subcategory_id):
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
    def get(self, request):
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
            return custom_response(response_data, "Product details retrieved successfully", status.HTTP_200_OK,
                                   "success")

        except Exception as e:
            data = {
                "error_message": f"An error occurred while retrieving product details: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")


class SimilarProductRecommendation(APIView):
    def get(self, request, product_id):
        try:
            current_product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return custom_response({}, "Product not found", status.HTTP_404_NOT_FOUND, "error")

        try:
            similar_products = Product.objects.filter(
                category = current_product,
                is_deleted='active',
                admin_status='approved',
            ).exclude(id=product_id)

            recommended_products = similar_products[:4]

            serializer = ProductSerializer(recommended_products, many=True)

            data = {
                "similar_products": serializer.data
            }

            return custom_response(data, "You might also like", status.HTTP_200_OK, "success")
        except Exception as e:
            data = {
                "error_message": f"An error occurred while while retrieving products you might like: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")


class ProductSearch(APIView):
    def get(self, request):
        search_query = request.query_params.get('search', '')
        try:
            products = Product.objects.filter(name__icontains=search_query)
            serializer = ProductSerializer(products, many=True)
            data = {
                "products": serializer.data
            }
            if not data["products"]:
                return custom_response(data, "No products Found", status.HTTP_404_NOT_FOUND, "error")
            return custom_response(data, "Products by Search", status.HTTP_200_OK, "success")
        except Exception as e:
            data = {
                "error_message": f"An error occurred while searching products: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")


#class ProductFilter(APIView):
    #def get(self, request):
        #try:
           # category_id = request.query_params.get('category_id')
            #subcategory_id = request.query_params.get('category_id')
            #min_price = request.query_params.get('min_price')
            #max_price = request.query_params.get('max_price')
            #condition = request.query_params.get('condition')
            #buying_format = request.query_params.get('buying_format')
            #item_location = request.query_params.get('item_location')
            #show_only = request.query_params.get('show_only')

            #products = Product.objects.all()

            #if category_id:
            #   products = products.filter(category=category_id)

            #if subcategory_id:
            #    products = products.filter(subcategory=subcategory_id)

            #if min_price:
            #   products = products.filter(price__gte=min_price)

            # if max_price:
            #   products = products.filter(price__lte=max_price)

            #if condition:
                #products = products.filter(condition=condition)

            #if buying_format:
                #products = products.filter(buying_format=buying_format)

            # if item_location:
                #products = products.filter(item_location=item_location)

            #if show_only:
            #   products = products.filter(show_only=show_only)

            #serializer = ProductSerializer(products, many=True)

            #data = {
            #    "products": serializer.data
            #}

            #if not data["products"]:
            # return custom_response(data, "No products found", status.HTTP_404_NOT_FOUND, "error")

            #return custom_response(data, "Filtered Products", status.HTTP_200_OK, "success")

            #except Exception as e:
            #data = {
            #   "error_message": f"An error occurred while filtering products: {str(e)}",
            #}
            #return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")

class FavouriteProductList(APIView):
    def get(self, request):
        user = request.user
        try:
            favourite_products = FavouriteProduct.objects.filter(user=user)
            serializer = FavouriteProductSerializer(favourite_products, many=True)
            data = {
                "favourite_products": serializer.data
            }
            return custom_response(data, "List of Favourite products", status.HTTP_200_OK, "success")
        except Exception as e:
            data = {
                "error_message": f"An error occurred while retrieving favorite products: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")

    def post(self, request):
        data = request.data
        data['user'] = request.user  # Set the current user as the owner
        serializer = FavouriteProductSerializer(data=data)
        try:
            if serializer.is_valid():
                serializer.save()
                data = {
                    "favorite_product": serializer.data
                }
                return custom_response(data, "Favorite product added", status.HTTP_201_CREATED, "success")
            return custom_response(serializer.errors, "Bad request", status.HTTP_400_BAD_REQUEST, "error")
        except Exception as e:
            data = {
                "error_message": f"An error occurred while adding a favorite product: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")


class FavouriteProductDetail(APIView):
    def delete(self, request, favorite_product_id):
        user = request.user
        try:
            favorite_product = get_object_or_404(FavouriteProduct, id=favorite_product_id, user=user)
            favorite_product.delete()
            return custom_response({}, "Favorite product removed", status.HTTP_204_NO_CONTENT, "success")
        except Exception as e:
            data = {
                "error_message": f"An error occurred while removing a favorite product: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")



