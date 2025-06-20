from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from store.models import User

# Register your models here.

@admin.register(User)
class UserAdmin(ImportExportModelAdmin):
    list_display = ["id", "name", "email", "is_admin", "is_creator"]
    search_fields = ["name", "email"]
    list_filter = ["is_admin", "is_creator"]
    readonly_fields = ["password"]
    save_as = True
