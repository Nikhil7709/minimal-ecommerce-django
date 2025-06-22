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
    ViewCartAPIView,
    RemoveFromCartAPIView,
    CreateCategoryAPIView,
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
    path('cart/', ViewCartAPIView.as_view(), name='view-cart'),
    path('cart/remove/<int:product_id>/', RemoveFromCartAPIView.as_view(), name='remove-from-cart'),

    path('order/place/', PlaceOrderAPIView.as_view(), name='place-order'),

    path('admin/category/create/', CreateCategoryAPIView.as_view(), name='admin-category-create'),

]
