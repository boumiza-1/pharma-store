from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import (
    Product,
    ProductVariant,
    Order,
    OrderItem,
    Category,
)


# =========================================================
# HOME
# =========================================================

def home(request):

    products = Product.objects.all().order_by("-created_at")[:8]

    categories = Category.objects.all().order_by("name")

    return render(
        request,
        "store/home.html",
        {
            "products": products,
            "categories": categories,
        }
    )


# =========================================================
# PRODUCT LIST
# =========================================================

def product_list(request):

    search = request.GET.get(
        "search",
        ""
    ).strip()

    category_id = request.GET.get(
        "category",
        ""
    ).strip()

    products = Product.objects.all().order_by(
        "-created_at"
    )

    if search:

        products = products.filter(
            name__icontains=search
        )

    if category_id:

        products = products.filter(
            category_id=category_id
        )

    return render(
        request,
        "store/product_list.html",
        {
            "products": products,
        }
    )


# =========================================================
# CATEGORY LIST
# =========================================================

def category_list(request):

    categories = Category.objects.all().order_by(
        "name"
    )

    return render(
        request,
        "store/category_list.html",
        {
            "categories": categories,
        }
    )


# =========================================================
# PRODUCT DETAIL
# =========================================================

def product_detail(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    variants = product.variants.all()

    return render(
        request,
        "store/product_detail.html",
        {
            "product": product,
            "variants": variants,
        }
    )


# =========================================================
# ADD TO CART
# =========================================================

def add_to_cart(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    cart = request.session.get(
        "cart",
        {}
    )

    variant_id = request.POST.get(
        "variant_id"
    )

    requested_quantity = request.POST.get(
        "quantity",
        "1"
    )

    try:
        requested_quantity = int(
            requested_quantity
        )
    except (ValueError, TypeError):
        requested_quantity = 1

    if requested_quantity < 1:
        requested_quantity = 1

    # =====================================================
    # PRODUIT AVEC VARIANTE
    # =====================================================

    if variant_id:

        try:

            variant = ProductVariant.objects.get(
                id=variant_id,
                product=product
            )

        except ProductVariant.DoesNotExist:

            return redirect(
                "product_detail",
                product_id=product_id
            )

        cart_key = (
            f"{product_id}_{variant.id}"
        )

        current_item = cart.get(
            cart_key,
            {
                "product_id": product_id,
                "variant_id": variant.id,
                "quantity": 0,
            }
        )

        current_quantity = current_item.get(
            "quantity",
            0
        )

        new_quantity = (
            current_quantity
            + requested_quantity
        )

        if new_quantity <= variant.quantity:

            cart[cart_key] = {
                "product_id": product_id,
                "variant_id": variant.id,
                "quantity": new_quantity,
            }

        else:

            cart[cart_key] = {
                "product_id": product_id,
                "variant_id": variant.id,
                "quantity": variant.quantity,
            }

    # =====================================================
    # PRODUIT SANS VARIANTE
    # =====================================================

    else:

        cart_key = str(
            product_id
        )

        current_item = cart.get(
            cart_key,
            {
                "product_id": product_id,
                "variant_id": None,
                "quantity": 0,
            }
        )

        current_quantity = current_item.get(
            "quantity",
            0
        )

        new_quantity = (
            current_quantity
            + requested_quantity
        )

        if new_quantity <= product.quantity:

            cart[cart_key] = {
                "product_id": product_id,
                "variant_id": None,
                "quantity": new_quantity,
            }

        else:

            cart[cart_key] = {
                "product_id": product_id,
                "variant_id": None,
                "quantity": product.quantity,
            }

    request.session["cart"] = cart

    request.session.modified = True

    return redirect("cart")


# =========================================================
# CART
# =========================================================

def cart(request):

    cart_data = request.session.get(
        "cart",
        {}
    )

    cart_items = []

    total = 0

    for cart_key, cart_item in cart_data.items():

        product_id = cart_item.get(
            "product_id"
        )

        variant_id = cart_item.get(
            "variant_id"
        )

        quantity = cart_item.get(
            "quantity",
            0
        )

        try:

            product = Product.objects.get(
                id=product_id
            )

        except Product.DoesNotExist:

            continue

        variant = None

        if variant_id:

            try:

                variant = ProductVariant.objects.get(
                    id=variant_id,
                    product=product
                )

            except ProductVariant.DoesNotExist:

                continue

        subtotal = (
            product.price * quantity
        )

        total += subtotal

        cart_items.append(
            {
                "product": product,
                "variant": variant,
                "quantity": quantity,
                "subtotal": subtotal,
            }
        )

    return render(
        request,
        "store/cart.html",
        {
            "cart_items": cart_items,
            "total": total,
        }
    )


# =========================================================
# REMOVE FROM CART
# =========================================================

def remove_from_cart(
    request,
    product_id
):

    cart = request.session.get(
        "cart",
        {}
    )

    variant_id = request.POST.get(
        "variant_id"
    )

    if variant_id:

        cart_key = (
            f"{product_id}_{variant_id}"
        )

    else:

        cart_key = str(
            product_id
        )

    if cart_key in cart:

        del cart[cart_key]

    request.session["cart"] = cart

    request.session.modified = True

    return redirect("cart")


# =========================================================
# CHECKOUT
# =========================================================

def checkout(request):

    cart_data = request.session.get(
        "cart",
        {}
    )

    if not cart_data:

        return redirect("cart")

    cart_items = []

    total = 0

    # =====================================================
    # PREPARE CART
    # =====================================================

    for cart_key, cart_item in cart_data.items():

        product_id = cart_item.get(
            "product_id"
        )

        variant_id = cart_item.get(
            "variant_id"
        )

        quantity = cart_item.get(
            "quantity",
            0
        )

        try:

            product = Product.objects.get(
                id=product_id
            )

        except Product.DoesNotExist:

            continue

        variant = None

        # =================================================
        # VARIANTE
        # =================================================

        if variant_id:

            try:

                variant = ProductVariant.objects.get(
                    id=variant_id,
                    product=product
                )

            except ProductVariant.DoesNotExist:

                return render(
                    request,
                    "store/checkout.html",
                    {
                        "cart_items": cart_items,
                        "total": total,
                        "error": (
                            f"La variante du produit "
                            f"{product.name} "
                            f"n'existe plus."
                        ),
                    }
                )

            if quantity > variant.quantity:

                return render(
                    request,
                    "store/checkout.html",
                    {
                        "cart_items": cart_items,
                        "total": total,
                        "error": (
                            f"Stock insuffisant pour "
                            f"{product.name} - "
                            f"{variant.option_value}."
                        ),
                    }
                )

        # =================================================
        # SANS VARIANTE
        # =================================================

        else:

            if quantity > product.quantity:

                return render(
                    request,
                    "store/checkout.html",
                    {
                        "cart_items": cart_items,
                        "total": total,
                        "error": (
                            f"Stock insuffisant pour "
                            f"{product.name}."
                        ),
                    }
                )

        subtotal = (
            product.price * quantity
        )

        total += subtotal

        cart_items.append(
            {
                "product": product,
                "variant": variant,
                "quantity": quantity,
                "subtotal": subtotal,
            }
        )

    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        customer_name = request.POST.get(
            "customer_name",
            ""
        ).strip()

        phone = request.POST.get(
            "phone",
            ""
        ).strip()

        address = request.POST.get(
            "address",
            ""
        ).strip()

        city = request.POST.get(
            "city",
            ""
        ).strip()

        if (
            not customer_name
            or not phone
            or not address
            or not city
        ):

            return render(
                request,
                "store/checkout.html",
                {
                    "cart_items": cart_items,
                    "total": total,
                    "error": (
                        "Veuillez remplir "
                        "tous les champs."
                    ),
                }
            )

        # =================================================
        # FINAL STOCK CHECK
        # =================================================

        for cart_key, cart_item in cart_data.items():

            product_id = cart_item.get(
                "product_id"
            )

            variant_id = cart_item.get(
                "variant_id"
            )

            quantity = cart_item.get(
                "quantity",
                0
            )

            try:

                product = Product.objects.get(
                    id=product_id
                )

            except Product.DoesNotExist:

                return render(
                    request,
                    "store/checkout.html",
                    {
                        "cart_items": cart_items,
                        "total": total,
                        "error": (
                            "Un produit du panier "
                            "n'existe plus."
                        ),
                    }
                )

            if variant_id:

                try:

                    variant = ProductVariant.objects.get(
                        id=variant_id,
                        product=product
                    )

                except ProductVariant.DoesNotExist:

                    return render(
                        request,
                        "store/checkout.html",
                        {
                            "cart_items": cart_items,
                            "total": total,
                            "error": (
                                f"La variante de "
                                f"{product.name} "
                                f"n'existe plus."
                            ),
                        }
                    )

                if quantity > variant.quantity:

                    return render(
                        request,
                        "store/checkout.html",
                        {
                            "cart_items": cart_items,
                            "total": total,
                            "error": (
                                f"Stock insuffisant pour "
                                f"{product.name} - "
                                f"{variant.option_value}."
                            ),
                        }
                    )

            else:

                if quantity > product.quantity:

                    return render(
                        request,
                        "store/checkout.html",
                        {
                            "cart_items": cart_items,
                            "total": total,
                            "error": (
                                f"Stock insuffisant pour "
                                f"{product.name}."
                            ),
                        }
                    )

        # =================================================
        # CREATE ORDER
        # =================================================

        order = Order.objects.create(

            user=(
                request.user
                if request.user.is_authenticated
                else None
            ),

            customer_name=customer_name,

            phone=phone,

            address=address,

            city=city,

            total=total,
        )

        # =================================================
        # ORDER ITEMS + STOCK
        # =================================================

        for cart_key, cart_item in cart_data.items():

            product_id = cart_item.get(
                "product_id"
            )

            variant_id = cart_item.get(
                "variant_id"
            )

            quantity = cart_item.get(
                "quantity",
                0
            )

            product = Product.objects.get(
                id=product_id
            )

            variant = None

            if variant_id:

                variant = ProductVariant.objects.get(
                    id=variant_id,
                    product=product
                )

            OrderItem.objects.create(

                order=order,

                product=product,

                variant=variant,

                quantity=quantity,

                price=product.price,
            )

            # =================================================
            # VARIANT STOCK
            # =================================================

            if variant:

                variant.quantity -= quantity

                variant.save(
                    update_fields=[
                        "quantity"
                    ]
                )

            # =================================================
            # PRODUCT STOCK
            # =================================================

            else:

                product.quantity -= quantity

                product.save(
                    update_fields=[
                        "quantity"
                    ]
                )

        # =================================================
        # CLEAR CART
        # =================================================

        request.session["cart"] = {}

        request.session.modified = True

        return redirect(
            "order_success",
            order_id=order.id
        )

    # =====================================================
    # GET
    # =====================================================

    return render(
        request,
        "store/checkout.html",
        {
            "cart_items": cart_items,
            "total": total,
        }
    )


# =========================================================
# ORDER SUCCESS
# =========================================================

def order_success(
    request,
    order_id
):

    order = get_object_or_404(
        Order,
        id=order_id
    )

    return render(
        request,
        "store/order_success.html",
        {
            "order": order,
        }
    )


# =========================================================
# REGISTER
# =========================================================

def register(request):

    if request.user.is_authenticated:

        return redirect(
            "product_list"
        )

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        password2 = request.POST.get(
            "password2",
            ""
        )

        if (
            not username
            or not email
            or not password
            or not password2
        ):

            return render(
                request,
                "store/register.html",
                {
                    "error": (
                        "Veuillez remplir "
                        "tous les champs."
                    )
                }
            )

        if password != password2:

            return render(
                request,
                "store/register.html",
                {
                    "error": (
                        "Les mots de passe "
                        "ne correspondent pas."
                    )
                }
            )

        if User.objects.filter(
            username=username
        ).exists():

            return render(
                request,
                "store/register.html",
                {
                    "error": (
                        "Ce nom d'utilisateur "
                        "existe déjà."
                    )
                }
            )

        if User.objects.filter(
            email=email
        ).exists():

            return render(
                request,
                "store/register.html",
                {
                    "error": (
                        "Cet email existe déjà."
                    )
                }
            )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(
            request,
            user
        )

        return redirect(
            "product_list"
        )

    return render(
        request,
        "store/register.html"
    )


# =========================================================
# LOGIN
# =========================================================

def login_view(request):

    if request.user.is_authenticated:

        return redirect(
            "product_list"
        )

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(
                request,
                user
            )

            return redirect(
                "product_list"
            )

        return render(
            request,
            "store/login.html",
            {
                "error": (
                    "Nom d'utilisateur "
                    "ou mot de passe incorrect."
                )
            }
        )

    return render(
        request,
        "store/login.html"
    )


# =========================================================
# LOGOUT
# =========================================================

def logout_view(request):

    if request.method == "POST":

        logout(request)

    return redirect(
        "product_list"
    )


# =========================================================
# MY ORDERS
# =========================================================

@login_required
def my_orders(request):

    orders = Order.objects.filter(
        user=request.user
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "store/my_orders.html",
        {
            "orders": orders,
        }
    )


# =========================================================
# CREATOR
# =========================================================

def creator(request):

    return render(
        request,
        "store/creator.html"
    )