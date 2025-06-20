from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from store.models import Category, Product, User

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

