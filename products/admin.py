from django.contrib import admin
from .models import *

admin.site.register(PizzaCategory)
admin.site.register(Pizza)
admin.site.register(Cart)
admin.site.register(CartItems)
