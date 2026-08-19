from django.contrib import admin

from .models import (
    Category,
    Product,
    ProductImage,
    ProductVariant,
    Order,
    OrderItem,
    Review,
)


# =========================================================
# PRODUCT IMAGES
# =========================================================

class ProductImageInline(admin.TabularInline):

    model = ProductImage

    extra = 1

    fields = (
        "image",
    )

    verbose_name = "Image supplémentaire"
    verbose_name_plural = "Images supplémentaires"


# =========================================================
# PRODUCT VARIANTS
# =========================================================

class ProductVariantInline(admin.TabularInline):

    model = ProductVariant

    extra = 1

    exclude = (
        "option_name",
    )

    fields = (
        "option_value",
        "quantity",
    )

    verbose_name = "Variante"
    verbose_name_plural = "Tailles / Pointures / Variantes"


# =========================================================
# PRODUCT
# =========================================================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "category",
        "price",
        "variant_type",
        "quantity",
        "total_stock",
        "has_variants",
        "created_at",
    )

    list_filter = (
        "category",
        "variant_type",
        "created_at",
    )

    search_fields = (
        "name",
        "description",
    )

    fields = (
        "category",
        "name",
        "description",
        "price",
        "variant_type",
        "quantity",
        "delivery",
        "image",
    )

    inlines = [
        ProductVariantInline,
        ProductImageInline,
    ]


# =========================================================
# CATEGORY
# =========================================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "description",
    )

    search_fields = (
        "name",
    )


# =========================================================
# ORDER ITEM INLINE
# =========================================================

class OrderItemInline(admin.TabularInline):

    model = OrderItem

    extra = 0

    readonly_fields = (
        "product",
        "variant",
        "quantity",
        "price",
    )


# =========================================================
# ORDER
# =========================================================

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
        "created_at",
    )

    search_fields = (
        "customer_name",
        "phone",
        "city",
    )

    inlines = [
        OrderItemInline,
    ]


# =========================================================
# REVIEW
# =========================================================

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "product",
        "rating",
        "created_at",
    )

    list_filter = (
        "rating",
        "created_at",
    )

    search_fields = (
        "user__username",
        "product__name",
        "comment",
    )