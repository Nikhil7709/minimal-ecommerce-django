from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from store.models import Cart, CartItem, Category, Order, Product, User

# Register your models here.

@admin.register(User)
class UserAdmin(ImportExportModelAdmin):
    list_display = ["id", "name", "email", "is_admin", "is_creator"]
    search_fields = ["name", "email"]
    list_filter = ["is_admin", "is_creator"]
    readonly_fields = ["password"]
    save_as = True


@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    list_display = ["id", "name", "slug"]
    search_fields = ["name", "slug"]
    readonly_fields = ["created_by", "updated_by"]
    save_as = True


@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    list_display = ["id", "name", "price", "stock", "category", "created_by"]
    search_fields = ["name", "description"]
    list_filter = ["category"]
    readonly_fields = ["created_by", "updated_by"]
    save_as = True


@admin.register(Cart)
class CartAdmin(ImportExportModelAdmin):
    list_display = ["id", "user"]
    search_fields = ["user__name", "user__email"]
    readonly_fields = ["created_by", "updated_by"]
    save_as = True


@admin.register(CartItem)
class CartItemAdmin(ImportExportModelAdmin):
    list_display = ["id", "cart", "product", "quantity"]
    search_fields = ["product__name", "cart__user__email"]
    list_filter = ["product"]
    readonly_fields = ["created_by", "updated_by"]
    save_as = True


@admin.register(Order)
class (ImportExportModelAdmin):
    list_display = ["id", "user", "total_amount", "status", "ordered_at"]
    search_fields = ["user__email", "user__name"]
    list_filter = ["status"]
    readonly_fields = ["created_by", "updated_by"]
    save_as = True


