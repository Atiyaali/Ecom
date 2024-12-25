from django.shortcuts import render , redirect
from .models import Product
def product(request, slug):

     item = Product.objects.get(slug = slug)
     context = {
        'product' : item,
        'selected_size':"N"
     }
     if request.GET.get("size"):
        size = request.GET.get("size")
        price = item.price_by_size(size)
        context['selected_size'] = size
        context['updated_price'] = price

     return render(request , "product/product.html" , context)


    