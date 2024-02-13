from rest_framework import status
from utils import custom_response
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Category, SubCategory, Product, FavouriteProduct, Color, Size, ProductReview
from .serializers import (
    CategorySerializer, SubCategorySerializer, ProductSerializer, FavouriteProductSerializer, ColorSerializer,
    SizeSerializer, ProductReviewSerializer
)
from .permissions import IsAuthorOrReadOnly


class ProductListCategory(APIView):
    """
    API endpoint for retrieving a list of products by category.

        - Allows users to get a list of products based on the specified category.

    Handles GET requests for retrieving products by category ID.

        Args:
            request: The HTTP request object.
            category_id: The ID of the category for which products are requested.

        Returns:
            Response: JSON response containing a list of products in the specified category.

    """
    def get(self, request, category_id):
        try:
            products = Product.objects.filter(category=category_id)
            serializer = ProductSerializer(products, many=True)
            data = {
                "products": serializer.data
            }
            if not data["products"]:
                return custom_response(data, "No products found", status
                                       .HTTP_200_OK, "success")
            return custom_response(data, "List of Products by Category", status.HTTP_200_OK, "success")
        except Exception as e:
            data = {
                "error_message": f"An error occurred while retrieving products: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")


class ProductListSubCategory(APIView):
    """
    API endpoint for retrieving a list of products by subcategory.

        - Allows users to get a list of products based on the specified subcategory.

    Handles GET requests for retrieving products by subcategory ID.

        Args:
            request: The HTTP request object.
            subcategory_id: The ID of the subcategory for which products are requested.

        Returns:
            Response: JSON response containing a list of products in the specified subcategory.

    """
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
    """
    API endpoint for retrieving a list of all available categories.

        - Allows users to get a list of all categories present in the system.

    Handles GET requests for retrieving categories.

        Args:
            request: The HTTP request object.

        Returns:
            Response: JSON response containing a list of available categories.

    """
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
    """
    API endpoint for retrieving a list of all available subcategories.

        - Allows users to get a list of all subcategories present in the system.

    Handles GET requests for retrieving subcategories.

        Args:
            request: The HTTP request object.

        Returns:
            Response: JSON response containing a list of available subcategories.

    """
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
    """
    API endpoint for retrieving detailed information about a specific product.

        - Allows users to get details about a product, including its reviews, ratings, colors, and sizes.

    Handles GET requests for retrieving product details.

        Args:
            request: The HTTP request object.
            product_id: The ID of the product for which details are requested.

        Returns:
            Response: JSON response containing detailed information about the requested product.

    """
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
            }
            return custom_response(response_data, "Product details retrieved successfully", status.HTTP_200_OK,
                                   "success")

        except Exception as e:
            data = {
                "error_message": f"An error occurred while retrieving product details: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")


class SimilarProductRecommendation(APIView):
    """
    API endpoint for recommending similar products based on a given product.

       - Allows users to get recommendations for products similar to the specified product.

    Handles GET requests for recommending similar products.

       Args:
           request: The HTTP request object.
           product_id: The ID of the product for which similar products are recommended.

       Returns:
           Response: JSON response containing a list of recommended similar products.

    """
    def get(self, request, product_id):
        try:
            current_product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return custom_response({}, "Product not found", status.HTTP_200_OK, "success")

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
    """
    API endpoint for searching products based on a provided query.

        - Allows users to search for products by name using a search query.

    Handles GET requests for searching products.

        Args:
            request: The HTTP request object.

        Returns:
            Response: JSON response containing a list of products matching the search query.

    """
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


class ProductFilter(APIView):
    """
    API endpoint for filtering products based on various criteria.

       - Allows users to filter products by category, subcategory, price range, and other parameters.

    Handles GET requests for filtering products.

       Args:
           request: The HTTP request object.

       Returns:
           Response: JSON response containing a list of filtered products.

    """
    def get(self, request):
        try:
            category_id = request.query_params.get('category_id')
            subcategory_id = request.query_params.get('subcategory_id')
            min_price = request.query_params.get('min_price')
            max_price = request.query_params.get('max_price')
            condition = request.query_params.get('condition')
            buying_format = request.query_params.get('buying_format')
            item_location = request.query_params.get('item_location')
            show_only = request.query_params.get('show_only')

            products = Product.objects.all()

            if category_id:
                products = products.filter(category=category_id)

            if subcategory_id:
                products = products.filter(subcategory=subcategory_id)

            if min_price:
                products = products.filter(price__gte=min_price)

            if max_price:
                products = products.filter(price__lte=max_price)

            if condition:
                products = products.filter(condition=condition)

            if buying_format:
                products = products.filter(buying_format=buying_format)

            if item_location:
                products = products.filter(item_location=item_location)

            if show_only:
                products = products.filter(show_only=show_only)

            serializer = ProductSerializer(products, many=True)

            data = {
                "products": serializer.data
            }

            if not data["products"]:
                return custom_response(data, "No products found", status.HTTP_404_NOT_FOUND, "error")

            return custom_response(data, "Filtered Products", status.HTTP_200_OK, "success")

        except Exception as e:
            data = {
                "error_message": f"An error occurred while filtering products: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")


class FavouriteProductList(APIView):
    def get(self, request):
        """
        API endpoint for retrieving a list of favorite products for the authenticated user.

            - Allows users to get a list of products marked as favorites.

        Handles GET requests for retrieving favorite products.

            Args:
                request: The HTTP request object.

            Returns:
                Response: JSON response containing a list of favorite products.

        """
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
        """
        API endpoint for adding a product to the user's favorites.

            - Allows users to add a product to their list of favorite products.

        Handles POST requests for adding a favorite product.

            Args:
                request: The HTTP request object.

            Returns:
                Response: JSON response indicating the success or failure of adding a favorite product.

        """
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
    """
    API endpoint for managing individual favorite products.

        - Allows users to add or remove products from their favorites.

    Handles DELETE requests for removing a favorite product.

        Args:
            request: The HTTP request object.
            favorite_product_id: The ID of the favorite product to be removed.

        Returns:
            Response: JSON response indicating the success or failure of removing a favorite product.

    """
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


class ProductReviewList(APIView):
    """
    API endpoint for retrieving a list of product reviews.

        - Allows users to get a list of reviews for products.

    Handles GET requests for retrieving product reviews.

        Args:
            request: The HTTP request object.

        Returns:
            Response: JSON response containing a list of product reviews.
    """
    permission_classes = [IsAuthorOrReadOnly]
    def get(self, request):
        try:
            product_reviews = ProductReview.objects.all()
            serializer = ProductReviewSerializer(product_reviews, many=True)
            data = {
                "product_reviews": serializer.data
            }
            return custom_response(data, "List of Product Reviews", status.HTTP_200_OK, "success")

        except Exception as e:
            data = {
                "error_message": f"An error occurred while retrieving product reviews: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")


class ProductReviewDetail(APIView):
    """
    API endpoint for managing individual product reviews.

        - Allows users to retrieve, add, update, or delete product reviews.

    Handles POST, GET, PUT, and DELETE requests for managing product reviews.

        Args:
            request: The HTTP request object.

        Returns:
            Response: JSON response containing information about the requested product review operation.

    """
    def post(self, request):
        """
        Add a new product review.

            - Allows users to add a new review for a product.

        Handles POST requests for adding a product review.

            Args:
                request: The HTTP request object.

            Returns:
                Response: JSON response indicating the success or failure of adding a product review.
        """
        data = request.data
        data['user'] = request.user

        serializer = ProductReviewSerializer(data=data)
        try:
            if serializer.is_valid():
                serializer.save()
                data = {
                    "product_review": serializer.data
                }
                return custom_response(data, "Product Review added", status.HTTP_201_CREATED, "success")
            return custom_response(serializer.errors, "Bad request", status.HTTP_400_BAD_REQUEST, "error")
        except Exception as e:
            data = {
                "error_message": f"An error occurred while adding a product review: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")

    def get_object(self, review_id):
        """
        Retrieve a specific product review.

            - Allows users to retrieve details of a specific product review.

            Args:
                review_id: The ID of the product review to be retrieved.

            Returns:
                productReview: The retrieved product review object.
                """
        return get_object_or_404(ProductReview, id=review_id)

    def delete(self, request, review_id):
        """
        Remove a product review.

            - Allows users to remove a product review.

        Handles DELETE requests for removing a product review.

            Args:
                request: The HTTP request object.
                review_id: The ID of the product review to be removed.

           Returns:
               esponse: JSON response indicating the success or failure of removing a product review.

        """
        try:
            review = self.get_object(review_id)
            review.delete()
            return custom_response({}, "Product Review removed", status.HTTP_204_NO_CONTENT, "success")
        except Exception as e:
            data = {
                "error_message": f"An error occurred while removing a product review: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")

    def put(self, request, review_id):
        """
        Update a product review.

            - Allows users to update a product review.

        Handles PUT requests for updating a product review.

            Args:
                request: The HTTP request object.
                review_id: The ID of the product review to be updated.

            Returns:
                Response: JSON response indicating the success or failure of updating a product review.

        """
        review = self.get_object(review_id)
        data = request.data
        serializer = ProductReviewSerializer(review, data=data)
        try:
            if serializer.is_valid():
                serializer.save()
                data = {
                    "product_review": serializer.data
                }
                return custom_response(data, "Product Review updated", status.HTTP_200_OK, "success")
            return custom_response(serializer.errors, "Bad request", status.HTTP_400_BAD_REQUEST, "error")
        except Exception as e:
            data = {
                "error_message": f"An error occurred while updating a product review: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")

