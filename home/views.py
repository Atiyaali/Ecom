from django.shortcuts import render
from product.models import Product  
from django.contrib.auth.decorators import login_required

def Index(request):
   context = {"products" : Product.objects.all() }
   return  render( request , "home/index.html" , context)