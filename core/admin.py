from django.contrib import admin

# Register your models here.
from core.models import Order, OrderItem, OrderFile

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(OrderFile)
