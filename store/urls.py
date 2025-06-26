from django.urls import path
from store.views import (
    AddToCartAPIView,
    PlaceOrderAPIView,
    ProductDetailAPIView,
    ProductListAPIView,
    ProductUpdateAPIView,
    RegisterAPIView,
    LoginAPIView,
    ProductCreateAPIView,
    ProductDeleteAPIView,
    SelectiveCheckoutAPIView,
    ViewCartAPIView,
    RemoveFromCartAPIView,
    CreateCategoryAPIView,
    CategoryListAPIView,
    CategoryUpdateAPIView,
    CategoryDeleteAPIView,
    logout_user,
    OrderCheckoutAPIView,
    OrderHistoryAPIView,
)
from django.views.generic import TemplateView



urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),

    path('create/', ProductCreateAPIView.as_view(), name='product-create'),
    path('', ProductListAPIView.as_view(), name='product-list'),
    path('<int:pk>/', ProductDetailAPIView.as_view(), name='product-detail'),
    path('product/<int:pk>/update/', ProductUpdateAPIView.as_view(), name='update-product'),
    path('products/<int:pk>/delete/', ProductDeleteAPIView.as_view(), name='product-delete'),

    path('cart/add/<int:product_id>/', AddToCartAPIView.as_view(), name='add-to-cart'),
    path('cart/', ViewCartAPIView.as_view(), name='view-cart'),
    path('cart/remove/<int:product_id>/', RemoveFromCartAPIView.as_view(), name='remove-from-cart'),

    path('order/place/', PlaceOrderAPIView.as_view(), name='place-order'),

    path('admin/category/create/', CreateCategoryAPIView.as_view(), name='admin-category-create'),
    path('admin/category/list/', CategoryListAPIView.as_view(), name='admin-category-list'),
    path('admin/category/update/<int:pk>/', CategoryUpdateAPIView.as_view(), name='admin-category-update'),
    path('admin/category/delete/<int:pk>/', CategoryDeleteAPIView.as_view(), name='admin-category-delete'),

    path('orders/history/', OrderHistoryAPIView.as_view(), name='order-history'),
    path('orders/checkout/', OrderCheckoutAPIView.as_view(), name='order-checkout'),
    path('orders/checkout/selected/', SelectiveCheckoutAPIView.as_view(), name='selective-checkout'),
    path('orders/history/', OrderHistoryAPIView.as_view(), name='order-history'),

    # UI paths
    path('register-ui/', TemplateView.as_view(template_name='registration.html'), name='register-ui'),
    path('login-ui/', TemplateView.as_view(template_name='login.html'), name='login-ui'),
    path('home/', TemplateView.as_view(template_name='home.html'), name='home'),
    path('product-ui/', TemplateView.as_view(template_name='product_detail.html'), name='product-ui'),
    path('cart-ui/', TemplateView.as_view(template_name='cart.html'), name='cart-ui'),
    path('checkout-ui/', TemplateView.as_view(template_name="checkout.html"), name="checkout-ui"),


]
