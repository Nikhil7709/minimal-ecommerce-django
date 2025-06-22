from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from store.models import Cart, CartItem, Category, Order, OrderItem, Product
from store.permissions import IsAdminOrProductCreator, IsAdminUser
from store.serializers import (
    CategorySerializer,
    LoginSerializer,
    ProductCreateSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
    RegisterSerializer,
)
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


# Create your views here.

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class RegisterAPIView(APIView):
    """
    API view for user registration.
    Handles user registration by validating input data and creating a new user.
    """
    def post(self, request):
        # Validate the request data using the RegisterSerializer
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = get_tokens_for_user(user)
            return Response(
                {
                    'message': 'Registration successful',
                    'user': {
                        'email': user.email,
                        'name': user.name,
                    },
                    'token': token
                }, 
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(email=email, password=password)
            if user:
                token = get_tokens_for_user(user)
                return Response(
                    {
                        'message': 'Login successful',
                        'token': token
                    },
                    status=status.HTTP_200_OK
                )
            return Response(
                {
                    'error': 'Invalid credentials'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class ProductCreateAPIView(APIView):
    """
    API view for creating a new product.
    Handles product creation by validating input data and saving the product.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Validate the request data using the ProductCreateSerializer
        serializer = ProductCreateSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save()
            product.created_by = request.user.email
            product.updated_by = request.user.email
            product.save()
            return Response(
                {
                    'message': 'Product created successfully',
                    'product': ProductDetailSerializer(product).data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class ProductListAPIView(APIView):
    """
    API view for listing all products.
    Retrieves all products from the database and returns them in a serialized format.
    """
    def get(self, request):
        # Retrieve all products and serialize them
        products = Product.objects.all()
        serializer = ProductListSerializer(products, many=True)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class ProductDetailAPIView(APIView):
    def get(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response(
                {
                    'error': 'Product not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProductDetailSerializer(product)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class ProductUpdateAPIView(APIView):
    """
    API view for updating a product.
    Only the admin or the user who created the product can update it.
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminOrProductCreator]

    def put(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response(
                {
                    'error': 'Product not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(request, product)

        serializer = ProductCreateSerializer(
            product, 
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            updated_product = serializer.save()
            updated_product.updated_by = request.user.email
            updated_product.save()
            return Response(
                {
                    'message': 'Product updated successfully',
                    'product': ProductDetailSerializer(updated_product).data
                },
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class ProductDeleteAPIView(APIView):
    """
    API view for deleting a product.
    Only the admin or the user who created the product can delete it.
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminOrProductCreator]

    def delete(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response(
                {
                    'error': 'Product not found'
                },
            status=status.HTTP_404_NOT_FOUND
        )

        self.check_object_permissions(request, product)

        product.delete()
        return Response(
            {
                'message': 'Product deleted successfully'
            },
            status=status.HTTP_204_NO_CONTENT
        )


class AddToCartAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {
                    "error": "Product not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        cart, created = Cart.objects.get_or_create(user=request.user)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': 1}
        )

        if not created:
            cart_item.quantity += 1
            cart_item.save()

        return Response(
            {
                "message": "Product added to cart successfully"
            },
            status=status.HTTP_200_OK
        )


class ViewCartAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response(
                {
                    "cart": []
                },
                status=status.HTTP_200_OK
            )

        items = CartItem.objects.filter(cart=cart)
        data = [
            {
                "product": item.product.name,
                "quantity": item.quantity,
                "price": item.product.price,
                "total": item.quantity * item.product.price
            }
            for item in items
        ]
        return Response(
            data,
            status=status.HTTP_200_OK
        )


class RemoveFromCartAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, product_id):
        try:
            cart = Cart.objects.get(user=request.user)
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return Response(
                {
                    "error": "Item not found in cart"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        cart_item.delete()
        return Response(
            {
                "message": "Item removed from cart"
            },
            status=status.HTTP_200_OK
        )


class PlaceOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        user = request.user

        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response(
                {
                    "error": "Cart is empty"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_items = CartItem.objects.filter(cart=cart)
        if not cart_items.exists():
            return Response(
                {
                    "error": "Cart has no items"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        total_amount = 0
        order_items_data = []

        # Step 1: Check stock availability
        for item in cart_items:
            if item.product.stock < item.quantity:
                return Response(
                    {
                        "error": f"Not enough stock for {item.product.name}. Available: {item.product.stock}"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Step 2: Create Order
        order = Order.objects.create(
            user=user,
            total_amount=0,  # temporary, will be updated below
            status="PENDING",
            created_by=user.email,
            updated_by=user.email
        )

        # Step 3: Create OrderItems and deduct stock
        for item in cart_items:
            price = item.product.price
            quantity = item.quantity
            subtotal = price * quantity
            total_amount += subtotal

            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=quantity,
                price_at_order_time=price,
                created_by=user.email,
                updated_by=user.email
            )

            # Deduct stock
            item.product.stock -= quantity
            item.product.save()

        # Update total amount
        order.total_amount = total_amount
        order.save()

        # Step 4: Clear cart
        cart_items.delete()

        return Response(
            {
                "message": "Order placed successfully",
                "order_id": order.id,
                "total_amount": float(order.total_amount),
                "status": order.status
            },
            status=status.HTTP_201_CREATED
        )


@method_decorator(csrf_exempt, name='dispatch')
class CreateCategoryAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            category = serializer.save()
            category.created_by = request.user.email
            category.updated_by = request.user.email
            category.save()
            return Response(
                {
                    "message": "Category created",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class CategoryListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(
            categories,
            many=True
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class CategoryUpdateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def put(self, request, pk):
        try:
            category = Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return Response(
                {
                    "error": "Category not found"
                },
            status=status.HTTP_404_NOT_FOUND
        )

        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            updated_category = serializer.save()
            updated_category.updated_by = request.user.email
            updated_category.save()
            return Response(
                {
                    "message": "Category updated",
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

