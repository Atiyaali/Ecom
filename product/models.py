from django.db import models
from Base.models import BaseModel
from django.utils.text import slugify
import stripe
from django.conf import settings
class Catagory(BaseModel):
    catagory_name= models.CharField(max_length=100)
    slug = models.SlugField(unique=True,null=True, blank=True)
    catagory_image = models.ImageField(upload_to="catagories")
    def save(self, *args, **kwargs):
        self.slug = slugify(self.catagory_name)
        super(Catagory,self).save(*args, **kwargs)
    def __str__(self) -> str:
        return self.catagory_name

class  ColorVariant(BaseModel):
    color_name = models.CharField(max_length=100 , null=True , blank=True)
    price = models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.color_name
class  SizeVariant(BaseModel):
    size_name = models.CharField(max_length=100 , null=True , blank=True)
    price = models.IntegerField(default=0)
    
    def __str__(self) -> str:
        return self.size_name   
    
class Product(BaseModel):
    product_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True,null=True, blank=True)
    product_catagory = models.ForeignKey(Catagory , on_delete=models.CASCADE)
    size_variant = models.ManyToManyField(SizeVariant)
    color_variant = models.ManyToManyField(ColorVariant)
    product_price =  models.IntegerField()
    product_description = models.TextField()

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)
    #     default_size_variant, created = SizeVariant.objects.get_or_create(size_name="N")
    #     self.size_variant.add(default_size_variant)  
    #     super().save(*args, **kwargs)
    def __str__(self) -> str:
        return self.product_name
    
    def price_by_size(self , size):
        price = SizeVariant.objects.get(size_name = size).price
        return self.product_price + price

class ProductImages(BaseModel):
    product = models.ForeignKey(Product ,on_delete=models.CASCADE ,  related_name="ProductImages")
    product_image= models.ImageField(upload_to="ProductImages")
  
class coupen(BaseModel):
    coupen_code = models.CharField(max_length=100)
    is_expired = models.BooleanField(default=False)
    discount = models.IntegerField(default=100)
    minimum_amount= models.IntegerField(default=500)


