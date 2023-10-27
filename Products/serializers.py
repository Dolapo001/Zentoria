from rest_framework import serializers
from .models import Category, Style, SubCategory, Product, ProductReview, FavouriteProduct, Size, Color


class StyleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Style
        fields = '__all__'


class ProductReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    style = StyleSerializer()
    reviews = ProductReviewSerializer(many=True)

    class Meta:
        model = Product
        fields = '__all__'


class FavouriteProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavouriteProduct
        fields = '__all__'


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ('id', 'name', 'hex_code')


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ('id', 'name', 'abbreviation')
