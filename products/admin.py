from django.contrib import admin

from products.models import Basket, Product, ProductCategory

admin.site.register(ProductCategory)


@admin.register(Product)  # декоратор регистрирует модель Product
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'quantity', 'category']
    fields = ['name', 'description', ('price', 'quantity'), 'image', 'category']
    search_fields = ['name']
    ordering = ['name']  # фильтрация по названию


class BasketAdmin(admin.TabularInline):
    model = Basket
    list_display = ['product', 'quantity']
    readonly_fields = ['created_timestamp']
    extra = 0
