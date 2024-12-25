from django.contrib import admin
from .models import * 
admin.site.register(Catagory)

class ProductImageAdmin(admin.StackedInline):
    model = ProductImages
class ProductAdmin(admin.ModelAdmin):
    list_display = ["product_name" ]
    inlines= [ProductImageAdmin]
@admin.register(SizeVariant)
class SizeVariantAdmin(admin.ModelAdmin):
    list_display = ["size_name", "price"]
    model = SizeVariant
@admin.register(ColorVariant)
class ColorVariantAdmin(admin.ModelAdmin):
    list_display = ["color_name", "price"]
    model = ColorVariant
admin.site.register(Product , ProductAdmin)
admin.site.register(ProductImages)
admin.site.register(coupen)