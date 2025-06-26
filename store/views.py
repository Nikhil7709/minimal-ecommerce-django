from decimal import Decimal
from django.shortcuts import redirect
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from libs.response import APIResponse
from store import STATUSCHOICES
from store.models import Cart, CartItem, Category, Order, OrderItem, Product
from store.permissions import IsAdminOrProductCreator, IsAdminUser
from store.serializers import (
    CategorySerializer,
    LoginSerializer,
    OrderSerializer,
    ProductCreateSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
    RegisterSerializer,
    OrderHistorySerializer,
)
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.parsers import MultiPartParser, FormParser


# Create your views here.

from datetime import timedelta

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

            return APIResponse(
                message="Registration successful",
                data={
                    "email": user.email,
                    "name": user.name,
                    "token": token
                },
                status_code=status.HTTP_201_CREATED
            )

        return APIResponse(
            success=False,
            message="Validation failed",
            errors={
                "code": "validation_error",
                "message": "Invalid input data",
                "errors": serializer.errors
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )


class LoginAPIView(APIView):
    """
    API view for user login.
    Handles user authentication by validating input data and returning a JWT token.
    """
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(email=email, password=password)

            if user:
                token = get_tokens_for_user(user)
                return APIResponse(
                    success=True,
                    message="Login successful.",
                    data={
                        "token": token
                    },
                    status_code=status.HTTP_200_OK
                )

            return APIResponse(
                success=False,
                message="Login failed.",
                error_code="INVALID_CREDENTIALS",
                error_message="Invalid email or password.",
                error_fields=[],
                data={},
                status_code=status.HTTP_401_UNAUTHORIZED
            )

        return APIResponse(
            success=False,
            message="Invalid input.",
            error_code="VALIDATION_ERROR",
            error_message="Email or password is missing or malformed.",
            error_fields=serializer.errors,
            data={},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

def logout_user(request):
    """
    Handles user logout by invalidating the JWT token.
    Redirects to the login UI after successful logout.
    """
    return redirect('/api/store/login-ui/')


class ProductCreateAPIView(APIView):
    """
    API view for creating a new product.
    Handles product creation by validating input data and saving the product.
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]


    def post(self, request):
        # Validate the request data using the ProductCreateSerializer
        serializer = ProductCreateSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save()
            product.created_by = request.user.email
            product.updated_by = request.user.email
            product.save()

            return APIResponse(
                success=True,
                message="Product created successfully.",
                data={
                    "product": ProductDetailSerializer(product).data
                },
                status_code=status.HTTP_201_CREATED
            )

        return APIResponse(
            success=False,
            message="Product creation failed.",
            error_code="VALIDATION_ERROR",
            error_message="Invalid product data provided.",
            error_fields=serializer.errors,
            data={},
            status_code=status.HTTP_400_BAD_REQUEST
        )


class ProductListAPIView(APIView):
    """
    API view for listing all products.
    Retrieves all products from the database and returns them in a serialized format.
    """
    # TODO: Add pagination to the product list
    def get(self, request):
        # Retrieve all products and serialize them
        products = Product.objects.all()
        serializer = ProductListSerializer(products, many=True)

        return APIResponse(
            success=True,
            message="Product list fetched successfully.",
            data={
                "products": serializer.data
            },
            status_code=status.HTTP_200_OK
        )


class ProductDetailAPIView(APIView):
    """ API view for retrieving product details."""
    def get(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return APIResponse(
                success=False,
                message="Product not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                data={}
            )

        serializer = ProductDetailSerializer(product)
        filtered_data = {
            "id": serializer.data["id"],
            "name": serializer.data["name"],
            "price": serializer.data["price"],
            "stock": serializer.data["stock"],
            "description": serializer.data["description"],
            "category": serializer.data["category_name"],
            "image": serializer.data["image"]
        }

        return APIResponse(
            success=True,
            message="Product fetched successfully.",
            data={"product": filtered_data},
            status_code=status.HTTP_200_OK
        )


class ProductUpdateAPIView(APIView):
    """
    API view for updating a product.
    Only the admin or the user who created the product can update it.
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminOrProductCreator]
    parser_classes = [MultiPartParser, FormParser]

    def put(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return APIResponse(
                success=False,
                message="Product not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                data={}
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

            filtered_data = {
                "id": updated_product.id,
                "name": updated_product.name,
                "price": str(updated_product.price),
                "stock": updated_product.stock,
            }

            return APIResponse(
                success=True,
                message="Product updated successfully.",
                data={
                    "product": filtered_data
                },
                status_code=status.HTTP_200_OK
            )
        return APIResponse(
            success=False,
            message="Validation failed.",
            error_fields=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
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
            return APIResponse(
                success=False,
                message="Product not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                data={}
            )

        self.check_object_permissions(request, product)

        product.delete()
        return APIResponse(
            success=True,
            message="Product deleted successfully.",
            data={},
            status_code=status.HTTP_204_NO_CONTENT
        )


class AddToCartAPIView(APIView):
    """
    API view for adding a product to the cart.
    """
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

        cart, _ = Cart.objects.get_or_create(user=request.user)
        quantity = int(request.data.get("quantity", 1))

        # Check stock availability
        if product.stock < quantity:
            return Response(
                {
                    "error": "Not enough stock available"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create cart item
        cart_item = CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=quantity
        )

        # Decrease product stock
        product.stock -= quantity
        product.save()

        cart_data = {
            "product_id": product.id,
            "product_name": product.name,
            "quantity": cart_item.quantity,
        }

        return APIResponse(
            success=True,
            message="Product added to cart successfully.",
            data={
                "cart_item": cart_data
            },
            status_code=status.HTTP_201_CREATED
        )


class ViewCartAPIView(APIView):
    """API view for viewing the user's cart."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return APIResponse(
                success=True,
                message="Cart fetched successfully.",
                data={
                    "cart": []
                },
                status_code=status.HTTP_200_OK
            )

        items = CartItem.objects.filter(cart=cart)
        cart_data = [
            {
                "product_id": item.product.id,
                "product": item.product.name,
                "quantity": item.quantity,
                "price": str(item.product.price),
                "total": str(item.quantity * item.product.price),
                "image": item.product.image.url if item.product.image else None,
            }
            for item in items
        ]

        return APIResponse(
            success=True,
            message="Cart fetched successfully.",
            data={
                "cart": cart_data
            },
            status_code=status.HTTP_200_OK
        )


class RemoveFromCartAPIView(APIView):
    """API view for removing an item from the user's cart."""
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, product_id):
        try:
            cart = Cart.objects.get(user=request.user)
            cart_item = CartItem.objects.filter(cart=cart, product_id=product_id).first()

            if not cart_item:
                return APIResponse(
                    success=False,
                    message="Item not found in cart.",
                    status_code=status.HTTP_404_NOT_FOUND,
                    data={}
                )

            # Restore product stock
            product = cart_item.product
            product.stock += cart_item.quantity
            product.save()

            # Delete the cart item
            cart_item.delete()

            return APIResponse(
                success=True,
                message="Item removed from cart successfully.",
                data={},
                status_code=status.HTTP_200_OK
            )

        except Cart.DoesNotExist:
            return APIResponse(
                success=False,
                message="Cart does not exist.",
                status_code=status.HTTP_404_NOT_FOUND,
                data={}
            )


class PlaceOrderAPIView(APIView):
    """
    API view for placing an order.
    """
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
            total_amount=0,
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

        return APIResponse(
            success=True,
            message="Order placed successfully.",
            data={
                "order_id": str(order.id),
                "total_amount": float(order.total_amount),
                "status": order.status
            },
            status_code=status.HTTP_201_CREATED
        )


@method_decorator(csrf_exempt, name='dispatch')
class CreateCategoryAPIView(APIView):
    """API view for creating a new category."""
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            category = serializer.save()
            category.created_by = request.user.email
            category.updated_by = request.user.email
            category.save()

            filtered_data = {
                "id": category.id,
                "name": category.name,
                "slug": category.slug
            }

            return APIResponse(
                success=True,
                message="Category created successfully.",
                data={
                    "category": filtered_data
                },
                status_code=status.HTTP_201_CREATED
            )

        return APIResponse(
            success=False,
            message="Validation failed.",
            error_fields=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class CategoryListAPIView(APIView):
    """API view for listing all categories."""
     # TODO: Add pagination to the category list
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(
            categories,
            many=True
        )

        formatted_data = [
            {
                "id": category["id"],
                "name": category["name"],
                "slug": category["slug"]
            } for category in serializer.data
        ]

        return APIResponse(
            success=True,
            message="Category list fetched successfully.",
            data={
                "categories": formatted_data
            },
            status_code=status.HTTP_200_OK
        )


class CategoryUpdateAPIView(APIView):
    """API view for updating a category."""
    # Only admin users can update categories
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def put(self, request, pk):
        try:
            category = Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return APIResponse(
                success=False,
                message="Category not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                data={}
            )

        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            updated_category = serializer.save()
            updated_category.updated_by = request.user.email
            updated_category.save()

            filtered_data = {
                "id": updated_category.id,
                "name": updated_category.name,
                "slug": updated_category.slug,
            }

            return APIResponse(
                success=True,
                message="Category updated successfully.",
                data={"category": filtered_data},
                status_code=status.HTTP_200_OK
            )

        return APIResponse(
            success=False,
            message="Validation failed.",
            error_fields=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class CategoryDeleteAPIView(APIView):
    """API view for deleting a category."""
    # Only admin users can delete categories
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def delete(self, request, pk):
        try:
            category = Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return APIResponse(
                success=False,
                message="Category not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                data={}
            )

        category.delete()

        return APIResponse(
            success=True,
            message="Category deleted successfully.",
            data={},
            status_code=status.HTTP_204_NO_CONTENT
        )


class OrderHistoryAPIView(APIView):
    """
    Returns the list of past orders for the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(
            user=request.user
        ).order_by(
            '-ordered_at'
        )

        serializer = OrderHistorySerializer(
            orders, 
            many=True
        )

        return APIResponse(
            success=True,
            message="Order history fetched successfully.",
            data={
                "orders": serializer.data
            },
            status_code=status.HTTP_200_OK
        )


class OrderCheckoutAPIView(APIView):
    """
    Converts cart into order, clears cart, and returns order summary.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return APIResponse(
                success=False,
                message="Cart is empty.",
                status_code=status.HTTP_400_BAD_REQUEST,
                data={}
            )

        cart_items = CartItem.objects.filter(cart=cart)
        if not cart_items.exists():
            return APIResponse(
                success=False,
                message="Cart is empty.",
                status_code=status.HTTP_400_BAD_REQUEST,
                data={}
            )

        total_amount = Decimal('0.00')
        for item in cart_items:
            total_amount += item.product.price * item.quantity

        # Create Order
        order = Order.objects.create(
            user=request.user,
            total_amount=total_amount,
            status=STATUSCHOICES.PENDING
        )

        # Create OrderItems and update stock
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price_at_order_time=item.product.price
            )
            item.product.stock -= item.quantity
            item.product.save()

        # Clear cart
        cart_items.delete()

        serializer = OrderSerializer(order)
        return APIResponse(
            success=True,
            message="Order placed successfully.",
            data={
                "order": serializer.data
            },
            status_code=status.HTTP_201_CREATED
        )


class SelectiveCheckoutAPIView(APIView):
    """
    Checkout only selected products from the user's cart.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_ids = request.data.get("product_ids", [])

        if not isinstance(product_ids, list) or not product_ids:
            return APIResponse(
                success=False,
                message="product_ids must be a non-empty list.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return APIResponse(
                success=False,
                message="Cart not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        cart_items = CartItem.objects.filter(
            cart=cart,
            product_id__in=product_ids
        )

        if not cart_items.exists():
            return APIResponse(
                success=False,
                message="No matching items found in cart.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        total_amount = Decimal("0.00")
        for item in cart_items:
            total_amount += item.product.price * item.quantity

        # Create order
        order = Order.objects.create(
            user=request.user,
            total_amount=total_amount,
            status=STATUSCHOICES.PENDING
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price_at_order_time=item.product.price
            )

            # Reduce stock
            item.product.stock -= item.quantity
            item.product.save()

        # Remove only the checked-out items
        cart_items.delete()

        serializer = OrderSerializer(order)
        return APIResponse(
            success=True,
            message="Selected items checked out successfully.",
            data={
                "order": serializer.data
            },
            status_code=status.HTTP_201_CREATED
        )


class OrderHistoryAPIView(APIView):
    """
    Returns the list of past orders for the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(
            user=request.user
        ).order_by(
            '-ordered_at'
        )

        serializer = OrderSerializer(orders, many=True)

        return APIResponse(
            success=True,
            message="Order history fetched successfully.",
            data={
                "orders": serializer.data
            },
            status_code=status.HTTP_200_OK
        )
