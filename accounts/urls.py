
from django.urls import path
from accounts.views import Login , Register , Activate_account , add_to_cart , cart , remove_item , Coupen,Remove_coupen, Logout,Createcheckoutsession,Success,cart_checkout_session,webhook,Order , Payment , cartOrder , cartPayment

urlpatterns = [
    path('login', Login , name="login" ),
    path('logout', Logout , name="logout" ),
    path('register' ,Register , name="register"),
    path('activate/<email_token>' ,Activate_account , name="activate"),
    path('add-to-cart/<uid>' , add_to_cart , name="add_to_cart"),
    path('cart' , cart , name="cart"),
    path("delete/<item_uid>", remove_item , name="remove_cart"),
    path("coupen" , Coupen , name="coupen"),
    path("remove-coupen/<cart_id>" , Remove_coupen ,name="remove-coupen"),
    path("order/" , Order , name="order"),
    path("cartOrder" , cartOrder , name="cartOrder"),
    path("payment/" , Payment , name="payment"),
    path("cartPayment/" , cartPayment , name="cartpayment"),
    path('Createcheckoutsession' , Createcheckoutsession , name="Createcheckoutsession"),
    path('Success' , Success , name="Success"),
    path('cart_checkout_session' , cart_checkout_session , name="cart_checkout_session"),
    path('webhook' , webhook , name="webhook"),


]