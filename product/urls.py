from django.urls import path
from product.views import product

urlpatterns = [
path("<slug>", product , name="product")
]