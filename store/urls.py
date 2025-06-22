from django.urls import path
from store.views import (
    AddToCartAPIView,
    ProductDetailAPIView,
    ProductListAPIView,
    ProductUpdateAPIView,
    RegisterAPIView,
    LoginAPIView,
    ProductCreateAPIView,
    ProductDeleteAPIView,
)


urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('create/', ProductCreateAPIView.as_view(), name='product-create'),
    path('', ProductListAPIView.as_view(), name='product-list'),
    path('<int:pk>/', ProductDetailAPIView.as_view(), name='product-detail'),
    path('product/<int:pk>/update/', ProductUpdateAPIView.as_view(), name='update-product'),
    path('products/<int:pk>/delete/', ProductDeleteAPIView.as_view(), name='product-delete'),

    path('cart/add/<int:product_id>/', AddToCartAPIView.as_view(), name='add-to-cart'),
]
