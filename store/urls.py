
from django.urls import path
from store.views import ProductListAPIView, RegisterAPIView, LoginAPIView, ProductCreateAPIView

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('create/', ProductCreateAPIView.as_view(), name='product-create'),
    path('', ProductListAPIView.as_view(), name='product-list'),
]