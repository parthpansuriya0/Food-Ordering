from django.contrib import admin
from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static
from products.views import *

urlpatterns = [
    path('', home,name="home"),
    path('deals/', deals,name="deals"),
    path('add-cart/<pizza_uid>', add_cart,name="add_cart"),
    path('add-cart-deals    /<pizza_uid>', add_cart_d,name="add_cart_d"),
    path('cart/', cart,name="cart"),
    path('remove-cart-item/<cart_item_uid>/', remove_cart_item,name="remove_cart_item"),
    path('orders/', orders,name="orders"),
    path('create-payment-order/', create_payment_order, name='create_payment_order'),
    path('verify-payment/', verify_payment, name='verify_payment'),
    path('success/', success, name='success'),
    path('login/', login_page,name="login_page"),
    path('logout/', logout_page,name="logout_page"),
    path('register/', register_page,name="register_page"),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns() 