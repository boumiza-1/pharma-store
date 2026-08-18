from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import Product, Order, OrderItem, Category


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


def product_list(request):
    search = request.GET.get("search", "").strip()
    category_id = request.GET.get("category", "").strip()

    products = Product.objects.all().order_by("-created_at")

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


def category_list(request):
    categories = Category.objects.all().order_by("name")

    return render(
        request,
        "store/category_list.html",
        {
            "categories": categories,
        }
    )


def product_detail(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id
    )

    return render(
        request,
        "store/product_detail.html",
        {
            "product": product,
        }
    )


def add_to_cart(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id
    )

    cart = request.session.get("cart", {})

    product_id = str(product_id)

    current_quantity = cart.get(
        product_id,
        0
    )

    if current_quantity < product.quantity:
        cart[product_id] = current_quantity + 1

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("cart")


def cart(request):
    cart_data = request.session.get(
        "cart",
        {}
    )

    products = Product.objects.filter(
        id__in=cart_data.keys()
    )

    cart_items = []
    total = 0

    for product in products:

        quantity = cart_data.get(
            str(product.id),
            0
        )

        subtotal = product.price * quantity

        total += subtotal

        cart_items.append({
            "product": product,
            "quantity": quantity,
            "subtotal": subtotal,
        })

    return render(
        request,
        "store/cart.html",
        {
            "cart_items": cart_items,
            "total": total,
        }
    )


def remove_from_cart(request, product_id):

    cart = request.session.get(
        "cart",
        {}
    )

    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("cart")


@login_required
def checkout(request):

    cart_data = request.session.get(
        "cart",
        {}
    )

    if not cart_data:
        return redirect("cart")

    products = Product.objects.filter(
        id__in=cart_data.keys()
    )

    cart_items = []
    total = 0

    for product in products:

        quantity = cart_data.get(
            str(product.id),
            0
        )

        if quantity > product.quantity:
            return render(
                request,
                "store/checkout.html",
                {
                    "cart_items": cart_items,
                    "total": total,
                    "error": (
                        f"Stock insuffisant "
                        f"pour {product.name}."
                    )
                }
            )

        subtotal = product.price * quantity

        total += subtotal

        cart_items.append({
            "product": product,
            "quantity": quantity,
            "subtotal": subtotal,
        })

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

        if not customer_name or not phone or not address or not city:

            return render(
                request,
                "store/checkout.html",
                {
                    "cart_items": cart_items,
                    "total": total,
                    "error": (
                        "Veuillez remplir "
                        "tous les champs."
                    )
                }
            )

        # Vérification finale du stock
        for product in products:

            quantity = cart_data.get(
                str(product.id),
                0
            )

            if quantity > product.quantity:

                return render(
                    request,
                    "store/checkout.html",
                    {
                        "cart_items": cart_items,
                        "total": total,
                        "error": (
                            f"Stock insuffisant "
                            f"pour {product.name}."
                        )
                    }
                )

        # Création de la commande
        order = Order.objects.create(
    user=request.user if request.user.is_authenticated else None,
    customer_name=customer_name,
    phone=phone,
    address=address,
    city=city,
    total=total,
)

        # Création des lignes + diminution du stock
        for product in products:

            quantity = cart_data.get(
                str(product.id),
                0
            )

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price,
            )

            product.quantity -= quantity

            product.save(
                update_fields=["quantity"]
            )

        # Vider le panier
        request.session["cart"] = {}
        request.session.modified = True

        return redirect(
            "order_success",
            order_id=order.id
        )

    return render(
        request,
        "store/checkout.html",
        {
            "cart_items": cart_items,
            "total": total,
        }
    )


def order_success(request, order_id):

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


def register(request):

    if request.user.is_authenticated:
        return redirect("product_list")

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

        if not username or not email or not password or not password2:

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

        return redirect("product_list")

    return render(
        request,
        "store/register.html"
    )


def login_view(request):

    if request.user.is_authenticated:
        return redirect("product_list")

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

            return redirect("product_list")

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


def logout_view(request):

    if request.method == "POST":
        logout(request)

    return redirect("product_list")


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


def creator(request):
    return render(
        request,
        "store/creator.html"
    )