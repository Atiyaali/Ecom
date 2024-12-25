from django.db import models
from Base.models import BaseModel
from django.contrib.auth.models import User
# post_save  A signal that gets triggered after a model instance is saved
from django.db.models.signals import post_save 
# receiver: A decorator for connecting signals to functions.
from django.dispatch import receiver
from Base.emails import send_email_account_activation
from product.models import Product , SizeVariant , coupen
# uuid: A module for generating unique identifiers.
import uuid
class Account(BaseModel):
    user = models.OneToOneField(User , on_delete=models.CASCADE ,related_name="account")
    is_email_verified = models.BooleanField(default=False)
    email_token = models.CharField(max_length=100 , null= True , blank= True)
    profile_picture = models.ImageField( upload_to="ProfilePicture",null=True , blank=True)
    
    def get_cart_count(self):
        return CartItem.objects.filter(cart__user=self.user , cart__is_paid = False).count()


class Cart(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE )
    coupen = models.ForeignKey(coupen , on_delete=models.CASCADE , null=True , blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(null=True)
    def get_total_price(self):
        items = CartItem.objects.filter(cart=self,cart__is_paid=False)
        total_price = 0
        for item in items:
            total_price += item.product.product_price
            if item.size_variant:
                total_price += item.size_variant.price
            cart = item.cart
            coupen = cart.coupen
        if self.coupen:
                if self.coupen.minimum_amount <  total_price:        
                     total_price -= coupen.discount          
        return total_price


class CartItem(BaseModel):
    cart = models.ForeignKey(Cart , on_delete=models.CASCADE , related_name="CartItems")
    product = models.ForeignKey(Product , on_delete=models.SET_NULL ,blank=True , null=True)
    size_variant = models.ForeignKey(SizeVariant, on_delete=models.CASCADE , null=True , blank=True)
    def price_by_size(self):
        if self.size_variant:
            return self.product.product_price + self.size_variant.price
        return self.product.product_price

 
                

@receiver(post_save , sender= User)
def send_email_token( sender, instance , created , **kwarges):
    try:
        if created:
            email_token =   str(uuid.uuid4())
            Account.objects.create( user= instance ,email_token = email_token)
            email = instance.email          
            send_email_account_activation(email , email_token)
    except Exception as e :
        print(e)
        
class order(BaseModel):
    user =models.ForeignKey(User, on_delete=models.CASCADE , related_name="orders")
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    Price = models.IntegerField(null=True , blank=True)
    order_date = models.DateTimeField(auto_now_add=True)
    order_status = models.CharField(max_length=10, choices=ORDER_STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')

class Order_items(BaseModel):
    order = models.ForeignKey(order , on_delete=models.CASCADE , related_name="products")
    Product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=100 , null=True , blank=True)
class order_details(BaseModel):
    order = models.ForeignKey(order, on_delete=models.CASCADE)
    shipping_address = models.TextField()
    tracking_number = models.CharField(max_length=50 , null=True , blank=True)
    notes = models.TextField(null=True, blank=True)
