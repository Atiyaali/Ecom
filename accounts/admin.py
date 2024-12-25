from django.contrib import admin
from .models import Account , Cart , CartItem , order , order_details , Order_items
admin.site.register(Account)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(order)
admin.site.register(order_details)
admin.site.register(Order_items)
# Register your models here.
