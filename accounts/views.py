from django.shortcuts import render , redirect ,get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponseRedirect , HttpResponse
from django.contrib.auth import authenticate , login, logout
from .models import Account , Cart , CartItem , order ,order_details , Order_items
from product.models import Product , SizeVariant , coupen
from django.contrib.auth.decorators import login_required
from django.conf import settings
import stripe
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def Login(request):
    if request.method == "POST":
        email= request.POST.get("email")
        password= request.POST.get("password")
        user_obj = User.objects.filter(username = email)
        if not user_obj.exists():
            messages.warning(request, "Account not found")
            return HttpResponseRedirect(request.path_info)
        if  not user_obj[0].account.is_email_verified:
            messages.warning(request, "Please verify your account")
            return HttpResponseRedirect(request.path_info)
        user_obj = authenticate(username = email , password = password)
        if user_obj:
            login(request,user_obj)
            return redirect("/")
        else:
           messages.warning(request, "Invalid Credentials")
    return render(request , "accounts/login.html")
def Logout(request):
    logout(request)
    return redirect("login")

def Register(request):
    if request.method == "POST":
        f_name= request.POST.get("first_name")
        l_name= request.POST.get("last_name")
        email= request.POST.get("email")
        password= request.POST.get("password")
        user_obj = User.objects.filter(username = email)
        if user_obj.exists():
            messages.warning(request, "email already register ")
            return HttpResponseRedirect(request.path_info)
        user_obj =User.objects.create(first_name = f_name , last_name = l_name , username = email , email = email)
        user_obj.set_password(password)
        user_obj.save()
        messages.success(request, "email has been sent")
        return HttpResponseRedirect(request.path_info)
    return render(request , "accounts/register.html")

def Activate_account(request , email_token):
    try:
     user =Account.objects.get(email_token=email_token)
     user.is_email_verified = True
     user.save()
     return redirect('login')
    except Exception as e :
     return HttpResponse("invalid token")
    
@login_required(login_url="login")
def add_to_cart(request , uid):
   variant = request.GET.get('variant')
   item = Product.objects.get(uid= uid)
   user = request.user
   cart,_ = Cart.objects.get_or_create(user=user , is_paid = False)
   cart_item = CartItem.objects.create(cart = cart , product= item)
   if variant: 
         variant = request.GET.get('variant')
         size = SizeVariant.objects.get(size_name= variant)
         cart_item.size_variant = size
         cart_item.save()
   return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required(login_url="login")
def cart(request ):
    context = {}
    try:
      cart = Cart.objects.get(is_paid=False , user = request.user)
      cartitems= []
      cartitem=cart.CartItems.all()
      for item in cartitem:
        price = item.price_by_size()
        cartitems.append({"item":item , "price":price})
        final = cart.get_total_price()
        context = {
        'cartitem': cartitems,
        'final':final,
        'cart':cart,
            }
    
    except Exception as e:
        print(e)

    return render(request , "accounts/cart.html" , context)
@login_required(login_url="login")
def remove_item(request , item_uid):
    try:
         item = CartItem.objects.get(uid = item_uid )
         item.delete()
    
    except Exception as e:
          print(e)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required(login_url="login")
def Coupen(request):
    cart = Cart.objects.get(user = request.user , is_paid =False)
    total_price = cart.get_total_price()
    if request.method == 'POST':
        coupencode = request.POST.get("coupen")
        coupen_obj = coupen.objects.filter(coupen_code = coupencode)
        if not coupen_obj.exists():
            messages.warning(request, "Invalid Coupen.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        if cart.coupen:
            messages.warning(request, 'coupen already exists')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        if total_price < coupen_obj[0].minimum_amount:
            messages.warning(request, 'your cart total amount is minimum to apply coupen')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        if coupen_obj[0].is_expired:
            messages.warning(request, 'Your coupen is expired')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        cart.coupen = coupen_obj.first()
        cart.save()
        messages.success(request, 'coupen applied')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    context = {
            'coupen':coupen_obj,
        }
    return render(request , "accounts/cart.html" , context)   

@login_required(login_url="accounts/login")
def Remove_coupen(request , cart_id):
    cart = Cart.objects.get(uid=cart_id)
    cart.coupen = None
    cart.save()
    messages.success(request, 'Coupen Removed')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def Order(request):   
    product_id = request.GET.get("product_id")
    size = request.GET.get("size")  
    product = get_object_or_404(Product, uid=product_id) 
    # if u_price:
    #     price = u_price  
    # else:
    #     price = product.product_price

    if request.method == "POST":
        price = product.price_by_size(size)
        shipping_address = request.POST.get("shipping_address")
        tracking_number = request.POST.get("tracking_number")
        notes = request.POST.get("notes")
        new_order = order.objects.create(user=request.user, Price=price) 
        Order_items.objects.create(order=new_order,Product=product,size=size )     
        order_details.objects.create(
            order=new_order,
            shipping_address=shipping_address,
            tracking_number=tracking_number,
            notes=notes
        )
        return redirect("/accounts/payment?order_id=" + str(new_order.uid))

    return render(request, 'accounts/order.html', {'product': product ,'size':size})
def cartOrder(request):
    if request.method == "POST":
         cart = Cart.objects.get(user=request.user , is_paid= False)
         price = cart.get_total_price()
         shipping_address = request.POST.get("shipping_address")
         tracking_number = request.POST.get("tracking_number")
         notes = request.POST.get("notes")
         Order = order.objects.create(user=request.user ,Price=price )
         for item in cart.CartItems.all():
           Order_items.objects.create(order=Order , Product=item.product , size=item.size_variant)    
         order_details.objects.create(
            order=Order,
            shipping_address=shipping_address,
            tracking_number=tracking_number,
            notes=notes
        )
         return redirect("/accounts/cartPayment?order_id=" + str(Order.uid))
    
    return render(request, 'accounts/cartOrder.html')
def Payment(request):
    order_id = request.GET.get("order_id")
    Order = get_object_or_404(order, uid=order_id)
    return render(request , "accounts/payment.html" ,{'Order': Order})

def cartPayment(request):
    order_id = request.GET.get("order_id")
    Order = get_object_or_404(order, uid=order_id)
    return render(request , "accounts/cartPayment.html" ,{'Order': Order})

def Createcheckoutsession(request):
    if request.method == "POST":
        email = request.user.email
        OrderId = request.POST.get("OrderId")  
        Order = order.objects.get(uid=OrderId)
        product_item = Order.products.first()
        if product_item:
            Product = product_item.Product
        YOUR_DOMAIN = "http://127.0.0.1:8000/accounts"
        stripe.api_key = settings.STRIPE_SECRET_KEY
        metadata = {
            'session_type': 'single_product',
            'orderId':OrderId,
            # 'product_name': Product.product_name,
            # 'product_description': Product.product_description,
        }
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'unit_amount': Order.Price*100,
                    'currency': 'usd',
                    'product_data': {
                        'name': Product.product_name,
                        'description': Product.product_description,
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=YOUR_DOMAIN + '/Success',
            cancel_url=YOUR_DOMAIN + '/cancel',
            customer_email=email,
            metadata=metadata,
        )

        return redirect(checkout_session.url, code=303)

def Success(request):
    return render(request , "product/success.html")
def cancel(request):
    return render(request , "product/cancel.html")

def cart_checkout_session(request):
    email= request.user.email
    if request.method == "POST":
        OrderId = request.POST.get("Order")
        cart = get_object_or_404(Cart, is_paid=False, user=request.user)         
        metadata = {'session_type': 'cart_checkout'}
        cart_price = cart.get_total_price()
        metadata["orderId"] = OrderId
        # for index, item in enumerate(Order.products.all()):
        #     product_name = item.Product.product_name
        #     product_description = item.Product.product_description
            

        #     metadata[f'product_name_{index}'] = product_name
        #     metadata[f'product_description_{index}'] = product_description

        YOUR_DOMAIN = "http://127.0.0.1:8000/accounts"
        stripe.api_key = settings.STRIPE_SECRET_KEY
        checkout_session = stripe.checkout.Session.create(
            line_items = [{
            'price_data': {
                'unit_amount':cart_price * 100 ,  # convert to cents
                'currency': 'usd',
                'product_data': {
                    'name': 'Total Cart Amount',
                    'description': 'Total price of all items in the cart',
                },
            },
            'quantity': 1,
        }]
,
            mode='payment',
            success_url=YOUR_DOMAIN + '/Success',
            cancel_url=YOUR_DOMAIN + '/cancel',
            customer_email=email,
            metadata=metadata
        )

        return redirect(checkout_session.url, code=303)

@csrf_exempt
def webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return JsonResponse({'error': 'Invalid signature'}, status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_session(session,cart)

    return JsonResponse({'status': 'success'}, status=200)


    
def handle_checkout_session(session,cart):
    customer_email = session.get('customer_email')
    metadata = session['metadata']
    OrderId = metadata['orderId']
    Order = order.objects.get(uid=OrderId)
    email_subject = 'Your purchase is confirmed'
    email_message = 'Thank you for purchasing.\n'
    for item in Order.products.all():
            product_name = item.Product.product_name
            product_description = item.Product.product_description
            email_message += f'\nProduct: {product_name}\nDescription: {product_description}\n'


    if metadata['session_type'] == 'cart_checkout':
            user = User.objects.get(email=customer_email)
            cart = Cart.objects.get(user=user, is_paid=False)
            cart.is_paid = True
            cart.save()

    Order.payment_status = "completed"
    Order.save()
    send_mail(
            email_subject,
            email_message,
            'your_email@example.com', 
            [customer_email],
            fail_silently=False,
        )

    return JsonResponse({'status': 'success'}, status=200)