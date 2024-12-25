from django.urls import path
from home.views import Index 

urlpatterns = [
path("", Index , name="index")
]