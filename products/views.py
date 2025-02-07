from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
import razorpay
import json
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required(login_url="/login/")
def home(request):
    pizzas = Pizza.objects.all()
    contex = {'page':'Home','pizzas':pizzas}
    return render(request,'home.html',contex)

@login_required(login_url="/login/")
def deals(request):
    pizzas = Pizza.objects.all()
    contex = {'page':'Deals','pizzas':pizzas}
    return render(request,'deals.html',contex)

def login_page(request):

    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = User.objects.filter(username=username)
            if not user.exists():
                messages.warning(request, 'Email not found.')
                return redirect('login_page')

            user = authenticate(request,username=username,password=password)

            if user is not None:
                login(request,user) 
                return redirect('home')
            
            messages.warning(request, 'Wrong Password.')
            return redirect('login_page')
        except Exception as e:
            print(f"Error: {str(e)}")
            messages.warning(request, "Something went wrong.")
            return redirect('login_page')
        
    contex = {'page':'Login'}
    return render(request,'login_page.html',contex)

@login_required(login_url="/login/")
def logout_page(request):
    logout(request)
    return redirect('login_page')

def register_page(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            user1 = User.objects.filter(username=username)
            if user1.exists():
                messages.warning(request, 'Username is taken.')
                return redirect('register_page')
            
            user2 = User.objects.filter(email=email)
            if user2.exists():
                messages.warning(request, 'Email already exits.')
                return redirect('register_page')

            if password == confirm_password:
                user = User.objects.create(username = username,email = email)
                user.set_password(password)
                user.save()

                messages.success(request, 'Account Create Succesfully.')
                return redirect('login_page')
            else:
                messages.warning(request, 'Password and Confirm Password do not match.')
                return redirect('register_page')

        except Exception as e:
            messages.warning(request, "Something went wrong.")
            return redirect('register_page')
        
    contex = {'page':'Register'}
    return render(request,'register_page.html',contex)

@login_required(login_url="/login/")
def add_cart(request,pizza_uid):
    user = request.user

    pizza_obj = Pizza.objects.get(uid = pizza_uid)

    cart , _ = Cart.objects.get_or_create(user=user,is_paid = False)

    cart_items = CartItems.objects.create(
        cart = cart,
        pizza = pizza_obj
    )

    return redirect('home')

@login_required(login_url="/login/")
def add_cart_d(request,pizza_uid):
    user = request.user

    pizza_obj = Pizza.objects.get(uid = pizza_uid)

    cart , _ = Cart.objects.get_or_create(user=user,is_paid = False)

    cart_items = CartItems.objects.create(
        cart = cart,
        pizza = pizza_obj
    )

    return redirect('deals')

@login_required(login_url="/login/")
def cart(request):
    cart = Cart.objects.get(is_paid = False,user = request.user)
    total_amount = cart.get_cart_total() * 100
    contex = {'page':'Cart','carts':cart,'total_amount': total_amount, 'razorpay_key': settings.RAZORPAY_KEY_ID}
    
    return render(request,'cart.html',contex)

@login_required(login_url="/login/")
def remove_cart_item(request,cart_item_uid):
    try:
        CartItems.objects.get(uid = cart_item_uid).delete()

        return redirect('cart')
    except Exception as e:
        print(e)

@login_required(login_url="/login/")
def orders(request):
    order = Cart.objects.filter(is_paid = True,user=request.user)
    context = {'page':'Orders','order':order}
    return render(request,'order.html',context)

@login_required(login_url="/login/")
def success(request):
    return render(request,'success.html')

@login_required(login_url="/login/")
def create_payment_order(request):

    if request.method == 'GET':
        try:
            # Get user's cart
            cart = Cart.objects.get(user=request.user, is_paid=False)
            total = cart.get_cart_total() * 100  # Convert INR to paise

            # Initialize Razorpay client
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

            order_data = {
                'amount': total,  # Amount in paise
                'currency': 'INR',
                'payment_capture': '1',  # Auto capture
            }

            # Create an order on Razorpay
            order = client.order.create(data=order_data)
            order_id = order['id']

            return JsonResponse({'order_id': order_id, 'total_amount': total, 'razorpay_key': settings.RAZORPAY_KEY_ID})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@login_required(login_url="/login/")
def verify_payment(request):
    """Verify Razorpay payment signature and update the order status"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Received Data:", data)  # ✅ Debugging

            razorpay_payment_id = data.get('razorpay_payment_id')
            razorpay_order_id = data.get('razorpay_order_id')
            razorpay_signature = data.get('razorpay_signature')

            print(razorpay_payment_id)
            print(razorpay_order_id)
            print(razorpay_signature)

            if not razorpay_payment_id or not razorpay_order_id or not razorpay_signature:
                return JsonResponse({'error': 'Missing payment details'}, status=400)

            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

            # Verify payment signature
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }

            client.utility.verify_payment_signature(params_dict)
            print("Signature Verified ✅")  # ✅ Debugging

            # Get cart and update payment status
            cart = get_object_or_404(Cart, user=request.user, is_paid=False)
            cart.is_paid = True
            cart.save()
            print("Cart Updated ✅")  # ✅ Debugging

            return JsonResponse({'status': 'success'})  # ✅ Ensure JSON response

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({'error': 'Payment verification failed - Invalid signature'}, status=400)
        except Cart.DoesNotExist:
            return JsonResponse({'error': 'Cart not found or already paid'}, status=400)
        except Exception as e:
            print("Error:", str(e))  # ✅ Debugging
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=400)
