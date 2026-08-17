from django.db import models
from cloudinary.models import CloudinaryField


class Category(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    description = models.TextField(
        blank=True
    )

    def __str__(self):
        return self.name


class Product(models.Model):

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products"
    )

    name = models.CharField(
        max_length=200
    )

    description = models.TextField(
        blank=True
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    quantity = models.PositiveIntegerField(
        default=0
    )

    delivery = models.CharField(
        max_length=255,
        blank=True
    )

    # ==========================================
    # PRODUCT IMAGE - CLOUDINARY
    # ==========================================

    image = CloudinaryField(
        "image",
        folder="sportifano/products",
        blank=True,
        null=True
    )

    # ==========================================

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name


class ProductVariant(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants"
    )

    option_name = models.CharField(
        max_length=100
    )

    option_value = models.CharField(
        max_length=100
    )

    quantity = models.PositiveIntegerField(
        default=0
    )

    def __str__(self):
        return (
            f"{self.product.name} - "
            f"{self.option_name}: "
            f"{self.option_value}"
        )


class Order(models.Model):

    STATUS_CHOICES = [
        ("pending", "En attente"),
        ("preparing", "En préparation"),
        ("shipping", "En livraison"),
        ("delivered", "Livrée"),
        ("cancelled", "Annulée"),
    ]

    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="orders",
        null=True,
        blank=True,
    )

    customer_name = models.CharField(
        max_length=200
    )

    phone = models.CharField(
        max_length=30
    )

    address = models.TextField()

    city = models.CharField(
        max_length=100
    )

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"Commande #{self.id} - "
            f"{self.customer_name}"
        )


class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items"
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return (
            f"{self.product.name} x "
            f"{self.quantity}"
        )


class Review(models.Model):

    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    rating = models.PositiveSmallIntegerField()

    comment = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                name="unique_user_product_review"
            )
        ]

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.product.name}"
        )