from django.db import models
from cloudinary.models import CloudinaryField


# =========================================================
# CATEGORY
# =========================================================

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


# =========================================================
# PRODUCT
# =========================================================

class Product(models.Model):

    VARIANT_TYPE_CHOICES = [
        ("", "Aucune variante"),
        ("Taille", "Taille"),
        ("Pointure", "Pointure"),
        ("Couleur", "Couleur"),
        ("Autre", "Autre"),
    ]

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

    # -----------------------------------------------------
    # TYPE DE VARIANTE
    #
    # Exemple:
    # Taille
    # Pointure
    # Couleur
    # -----------------------------------------------------

    variant_type = models.CharField(
        max_length=100,
        choices=VARIANT_TYPE_CHOICES,
        blank=True,
        default=""
    )

    # -----------------------------------------------------
    # STOCK TOTAL
    #
    # Utilisé uniquement quand le produit n'a pas
    # de variantes.
    # -----------------------------------------------------

    quantity = models.PositiveIntegerField(
        default=0
    )

    delivery = models.CharField(
        max_length=255,
        blank=True
    )

    # -----------------------------------------------------
    # IMAGE PRINCIPALE
    # -----------------------------------------------------

    image = CloudinaryField(
        "image",
        folder="sportifano/products",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    # -----------------------------------------------------
    # Vérifier si le produit possède des variantes
    # -----------------------------------------------------

    @property
    def has_variants(self):
        return self.variants.exists()

    # -----------------------------------------------------
    # Stock disponible
    # -----------------------------------------------------

    @property
    def total_stock(self):

        if self.has_variants:

            return sum(
                variant.quantity
                for variant in self.variants.all()
            )

        return self.quantity

    # -----------------------------------------------------

    @property
    def is_in_stock(self):

        return self.total_stock > 0

    # -----------------------------------------------------

    def __str__(self):

        return self.name


# =========================================================
# PRODUCT IMAGES
# =========================================================

class ProductImage(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = CloudinaryField(
        "image",
        folder="sportifano/products"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):

        return f"Image - {self.product.name}"


# =========================================================
# PRODUCT VARIANTS
# =========================================================

class ProductVariant(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants"
    )

    # -----------------------------------------------------
    # ANCIEN CHAMP CONSERVÉ POUR COMPATIBILITÉ DATABASE
    #
    # Il n'est plus demandé dans Admin.
    # Il est rempli automatiquement depuis Product.variant_type
    # -----------------------------------------------------

    option_name = models.CharField(
        max_length=100,
        blank=True,
        editable=False
    )

    # -----------------------------------------------------
    # VALEUR DE LA VARIANTE
    #
    # Exemple:
    # S
    # M
    # L
    # XL
    #
    # ou:
    # 41
    # 42
    # 43
    # -----------------------------------------------------

    option_value = models.CharField(
        max_length=100
    )

    # -----------------------------------------------------
    # STOCK DE CETTE VARIANTE
    # -----------------------------------------------------

    quantity = models.PositiveIntegerField(
        default=0
    )

    class Meta:

        ordering = ["id"]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "product",
                    "option_name",
                    "option_value"
                ],
                name="unique_product_variant"
            )
        ]

    def save(self, *args, **kwargs):

        # Remplir automatiquement option_name
        if self.product:

            if self.product.variant_type:

                self.option_name = (
                    self.product.variant_type
                )

        super().save(*args, **kwargs)

    def __str__(self):

        variant_name = (
            self.option_name
            or self.product.variant_type
            or "Variante"
        )

        return (
            f"{self.product.name} - "
            f"{variant_name}: "
            f"{self.option_value} "
            f"({self.quantity})"
        )

    @property
    def is_in_stock(self):

        return self.quantity > 0


# =========================================================
# ORDER
# =========================================================

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


# =========================================================
# ORDER ITEM
# =========================================================

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

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        related_name="order_items",
        null=True,
        blank=True
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):

        if self.variant:

            variant_name = (
                self.variant.option_name
                or self.product.variant_type
                or "Variante"
            )

            return (
                f"{self.product.name} - "
                f"{variant_name}: "
                f"{self.variant.option_value} x "
                f"{self.quantity}"
            )

        return (
            f"{self.product.name} x "
            f"{self.quantity}"
        )


# =========================================================
# REVIEW
# =========================================================

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
                fields=[
                    "user",
                    "product"
                ],
                name="unique_user_product_review"
            )
        ]

    def __str__(self):

        return (
            f"{self.user.username} - "
            f"{self.product.name}"
        )