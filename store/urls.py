from django.urls import path

from .views import (
    home,
    product_list,
    category_list,
    product_detail,
    add_to_cart,
    cart,
    remove_from_cart,
    checkout,
    order_success,
    register,
    login_view,
    logout_view,
    my_orders,
    creator,
)

urlpatterns = [

    path(
        "",
        home,
        name="home"
    ),

    path(
        "products/",
        product_list,
        name="product_list"
    ),

    path(
        "categories/",
        category_list,
        name="category_list"
    ),

    path(
        "product/<int:product_id>/",
        product_detail,
        name="product_detail"
    ),

    path(
        "cart/",
        cart,
        name="cart"
    ),

    path(
        "cart/add/<int:product_id>/",
        add_to_cart,
        name="add_to_cart"
    ),

    path(
        "cart/remove/<int:product_id>/",
        remove_from_cart,
        name="remove_from_cart"
    ),

    path(
        "checkout/",
        checkout,
        name="checkout"
    ),

    path(
        "order-success/<int:order_id>/",
        order_success,
        name="order_success"
    ),

    path(
        "register/",
        register,
        name="register"
    ),

    path(
        "login/",
        login_view,
        name="login"
    ),

    path(
        "logout/",
        logout_view,
        name="logout"
    ),

    path(
        "my-orders/",
        my_orders,
        name="my_orders"
    ),
    path(
        "creator/", 
        creator,
          name="creator"),
]