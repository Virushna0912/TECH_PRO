from urllib import request
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render , redirect , get_object_or_404
from django.views import View
import razorpay
from . models import  Product , Customer , Cart , OrderPlaced ,Payment , Wishlist
from . forms import CustomerProfileForm, CustomerRegistrationForm
from django.contrib import messages
from django.db.models import Q
from django.conf import settings


# Create your views here.

def home(request):
     totalitem=0
     wishitem=0
     if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
     return render(request,"home.html",locals())

def about(request):
    totalitem=0
    wishitem=0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    return render(request,"about.html",locals())

def contact(request):
     totalitem=0
     wishitem=0
     if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
     return render(request,"contact.html",locals())

class CategoryView(View):
    def get(self,request,val):
     totalitem=0
     wishitem=0
     if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
        product = Product.objects.filter(category=val)
        title = Product.objects.filter(category=val).values('title')
        return render(request,"category.html",locals())

class CategoryTitle(View):
     def get(self,request,val):
        product = Product.objects.filter(title=val)
        title = Product.objects.filter(category=product[0].category).values('title')
        totalitem=0
        wishitem=0
        if request.user.is_authenticated:
           totalitem = len(Cart.objects.filter(user=request.user))
           wishitem = len(Wishlist.objects.filter(user=request.user))
        return render(request,"category.html",locals())

class ProductDetail(View):
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        wishlist = Wishlist.objects.none()  # Initialize wishlist as an empty queryset
        totalitem = 0
        wishitem = 0

        if request.user.is_authenticated:
            wishlist = Wishlist.objects.filter(Q(product=product) & Q(user=request.user))
            totalitem = Cart.objects.filter(user=request.user).count()
            wishitem = Wishlist.objects.filter(user=request.user).count()

        return render(request, "productdetails.html", {
            'product': product,
            'wishlist': wishlist,
            'totalitem': totalitem,
            'wishitem': wishitem,
        })
  
class CustomerRegistrationView(View):
    def get(self,request):
        form =CustomerRegistrationForm()
        totalitem=0
        wishitem=0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))
        return render(request,"customerregistration.html",locals())
    def post(self,request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Congratulations! User Registration Completed Sucessfully")
        else:
            messages.warning(request,"Invaild Input Data")
        return render(request,"customerregistration.html",locals())
 
class ProfileView(View):
    def get(self,request):
        form = CustomerProfileForm()
        totalitem=0
        wishitem=0
        if request.user.is_authenticated:
         totalitem = len(Cart.objects.filter(user=request.user))
         wishitem = len(Wishlist.objects.filter(user=request.user))
        return render(request,"profile.html",locals())
    def post(self,request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            mobile = form.cleaned_data['mobile']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']
            
            reg = Customer (user=user,name=name,locality=locality,mobile=mobile,city=city,state=state,zipcode=zipcode)
            reg.save()
            messages.success(request,"Congratulations! Profile Save Successfully")
        else:
            messages.warning(request,"Invalid data")
        return render(request,"profile.html",locals())

def address(request):
    add = Customer.objects.filter(user=request.user)
    totalitem=0
    wishitem=0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    return render(request,'address.html',locals())

class updateAddress(View):
    def get(self,request,pk):
        add = Customer.objects.get(pk=pk)
        form = CustomerProfileForm(instance=add)
        totalitem=0
        wishitem=0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))
        return render(request,"updateAddress.html",locals())
    def post(self,request,pk):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            add = Customer.objects.get(pk=pk)
            add.name = form.cleaned_data['name']
            add.locality = form.cleaned_data['locality']
            add.city = form.cleaned_data['city']
            add.mobile = form.cleaned_data['mobile']
            add.state = form.cleaned_data['state']
            add.zipcode = form.cleaned_data['zipcode']
            add.save()
            messages.success(request,"Congratulations! Profile Save Successfully")
        else:
            messages.warning(request,"Invalid data")
        return redirect("address")
    
def add_to_cart(request):
    user=request.user
    product_id=request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    Cart(user=user,product=product).save()
    return redirect("/cart")

def show_cart(request):
    user = request.user
    cart = Cart.objects.filter(user=user)
    amount = 0
    for p in cart:
        value = p.quantity * p.product.discounted_price
        amount = amount + value
    totalamount = amount + 40
    totalitem=0
    wishitem=0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    return render(request,'addtocart.html',locals())

class checkout(View):
    def get(self,request):
        totalitem=0
        wishitem=0
        if request.user.is_authenticated:
         totalitem = len(Cart.objects.filter(user=request.user))
         wishitem = len(Wishlist.objects.filter(user=request.user))
        user = request.user
        add = Customer.objects.filter(user=user)
        cart_items = Cart.objects.filter(user=user)
        famount = 0
        for p in cart_items:
            value = p.quantity * p.product.discounted_price
            famount = famount + value
            totalamount = famount + 40
            razoramount = int(totalamount * 100 )
            client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
            data = { "amount": razoramount, "currency": "INR", "receipt": "order_rcptid_12"}
            payment_response = client.order.create(data=data)
            print(payment_response)
            #{'amount': 3004000, 'amount_due': 3004000, 'amount_paid': 0, 'attempts': 0, 'created_at': 1723715569, 'currency': 'INR', 'entity': 'order', 'id': 'order_Ol8GSGr4yLGJkT', 'notes': [], 'offer_id': None, 'receipt': 'order_rcptid_12', 'status': 'created'}
            order_id = payment_response['id']
            order_status = payment_response['status']
            if order_status == 'created':
                payment = Payment(
                    user=user,
                    amount=totalamount,
                    razorpay_order_id=order_id,
                    razorpay_payment_status = order_status
                )
                payment.save()
        return render(request,'checkout.html',locals())
def payment_done(request):
     order_id=request.GET.get('order_id')
     payment_id=request.GET.get('payment_id')
     cust_id=request.GET.get('cust_id')
     #print("payment_done : oid = ",order_id," pid = ",payment_id," cid = ", cust_id)
     user=request.user
     #return redirect("orders")
     customer=Customer.objects.get(id=cust_id)
     #to update payment status and id
     payment=Payment.objects.get(razorpay_order_id=order_id)
     payment.paid = True
     payment.razorpay_payment_id = payment_id
     payment.save()
     #to save order
     cart=Cart.objects.filter(user=user)
     for c in cart:
         OrderPlaced(user=user,customer=customer,product=c.product,quantity=c.quantity,payment=payment).save()
         c.delete()
         return redirect("orders")
def orders(request):
    totalitem=0
    wishitem=0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    order_placed=OrderPlaced.objects.filter(user=request.user)
    return render(request,'orders.html',locals())
    
    
def plus_cart(request):
    if request.method =='GET':
        prod_id=request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q (user=request.user))
        c.quantity+=1
        c.save()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
            totalamount = amount + 40
        print(prod_id)
        data={
            'quantity' : c.quantity,
            'amount' : amount,
            'totalamount' : totalamount
            
        }
        return JsonResponse(data)
    
def minus_cart(request):
    if request.method =='GET':
        prod_id=request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q (user=request.user))
        c.quantity-=1
        c.save()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
            totalamount = amount + 40
        print(prod_id)
        data={
            'quantity' : c.quantity,
            'amount' : amount,
            'totalamount' : totalamount
            
        }
        return JsonResponse(data)
    
def remove_cart(request):
    if request.method =='GET':
        prod_id=request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q (user=request.user))
        c.delete()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
            totalamount = amount + 40
        print(prod_id)
        data={
            'amount' : amount,
            'totalamount' : totalamount
         }
        return JsonResponse(data)

def plus_wishlist(request):
    if request.method =='GET':
        prod_id=request.GET['prod_id']
        product=Product.objects.get(id=prod_id)
        user = request.user
        Wishlist(user=user,product=product).save()
        data={
            'message':'Wishlist Added Successfully',
        }
        return JsonResponse(data)

def minus_wishlist(request):
    if request.method == 'GET':
        prod_id=request.GET['prod_id']
        product=Product.objects.get(id=prod_id)
        user = request.user
        Wishlist.objects.filter(user=user,product=product).delete()
        data={
            'message':'Wishlist Removed Successfully',
        }
        return JsonResponse(data)

def search(request):
    query = request.GET['search']
    totalitem=0
    wishitem=0
    if request.user.is_authenticated:
       totalitem = len(Cart.objects.filter(user=request.user))
       wishitem = len(Wishlist.objects.filter(user=request.user))
    product = Product.objects.filter(Q(title__icontains=query))
    return render(request,"search.html",locals())

def logout(request):
    try:
        del request.session['user']
    except:
        return redirect('login')
    return redirect('login')

class WishlistView(View):
    def get(self, request):
         if not request.user.is_authenticated:
            
            return redirect('login')  # Redirect to login page if not authenticated
        
         wishlist_items = Wishlist.objects.filter(user=request.user)
         return render(request, 'wishlist.html', {'wishlist_items': wishlist_items})

def add_to_wishlist(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login')
    
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    return redirect('wishlist')

def remove_from_wishlist(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login')
    
    wishlist_item = get_object_or_404(Wishlist, user=request.user, product_id=product_id)
    wishlist_item.delete()
    return redirect('wishlist')