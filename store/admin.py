from django.contrib import admin
from .models import Category, Product, Order, OrderItem


# =========================
# CATEGORY
# =========================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description")
    search_fields = ("name",)


# =========================
# PRODUCT
# =========================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "category",
        "price",
        "quantity",
        "delivery",
        "created_at",
    )

    search_fields = ("name",)


# =========================
# ORDER ACTIONS
# =========================

@admin.action(description="Mettre en préparation")
def mark_preparing(modeladmin, request, queryset):
    queryset.update(status="preparing")


@admin.action(description="Mettre en livraison")
def mark_shipping(modeladmin, request, queryset):
    queryset.update(status="shipping")


@admin.action(description="Marquer comme livrée")
def mark_delivered(modeladmin, request, queryset):
    queryset.update(status="delivered")


@admin.action(description="Annuler la commande")
def mark_cancelled(modeladmin, request, queryset):
    queryset.update(status="cancelled")


@admin.action(description="Remettre en attente")
def mark_pending(modeladmin, request, queryset):
    queryset.update(status="pending")


# =========================
# ORDER
# =========================

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "customer_name",
        "phone",
        "city",
        "total",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "city",
    )

    search_fields = (
        "customer_name",
        "phone",
        "address",
    )

    actions = [
        mark_pending,
        mark_preparing,
        mark_shipping,
        mark_delivered,
        mark_cancelled,
    ]


# =========================
# ORDER ITEM
# =========================

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "order",
        "product",
        "quantity",
        "price",
    )

    search_fields = (
        "product__name",
        "order__customer_name",
    )