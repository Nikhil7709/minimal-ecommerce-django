from rest_framework import serializers
from store.models import Category, Order, OrderItem, Product, User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "name", "password"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "description", "price", "stock", "category", "image"]


class ProductDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = ["id", "name", "description", "price", "stock", "category_name", "image"]


class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock', 'image']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class ProductInOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "price"]


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductInOrderSerializer()

    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "price_at_order_time"]


class OrderHistorySerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ["id", "total_amount", "status", "ordered_at", "items"]

    def get_items(self, obj):
        order_items = OrderItem.objects.filter(order=obj)
        return OrderItemSerializer(
            order_items,
            many=True
        ).data


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "quantity", "price_at_order_time"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(
        source="store_orderitem_order", many=True, read_only=True
    )

    class Meta:
        model = Order
        fields = ["id", "total_amount", "status", "ordered_at", "items"]
