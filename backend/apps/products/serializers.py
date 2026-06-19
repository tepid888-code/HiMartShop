from rest_framework import serializers
from apps.products.models import Category, Product, ProductImage, ProductReview, ProductInventory, WishlistItem
from apps.users.serializers import UserSerializer


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'parent', 'children']
        read_only_fields = ['id']

    def get_children(self, obj):
        children = obj.children.all()
        return CategorySerializer(children, many=True).data


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary', 'order']
        read_only_fields = ['id']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'price', 'original_price', 'rating',
                  'review_count', 'category', 'store', 'is_active', 'created_at']
        read_only_fields = ['id', 'rating', 'review_count', 'created_at']


class ProductDetailSerializer(ProductSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    seller = UserSerializer(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'description', 'price', 'original_price',
                  'sku', 'condition', 'stock', 'sold', 'rating', 'review_count',
                  'images', 'seller', 'category', 'category_name', 'store', 'store_name',
                  'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'rating', 'review_count', 'sold', 'created_at', 'updated_at']


class ProductReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ProductReview
        fields = ['id', 'product', 'user', 'rating', 'title', 'comment',
                  'helpful_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'helpful_count', 'created_at', 'updated_at']


class WishlistSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = WishlistItem
        fields = ['id', 'product', 'added_at']
        read_only_fields = ['id', 'added_at']
