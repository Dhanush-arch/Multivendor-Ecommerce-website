from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.shortcuts import redirect
from django.utils import timezone
from .forms import CheckoutForm, CouponForm, RefundForm, RadioCheckoutForm
from .models import Item, OrderItem, OrdeItem, Order, BillingAddress, Payment, Coupon, Refund, Category, MiddleVariation, FinalVariation, Customer, Tax, Slide, Collection
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from core.models import CommentForm, Comment, ContactForm, Contact
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
import re
from django.contrib.admin.views.decorators import staff_member_required
import random
import string
from django.core.paginator import Paginator


def pdfView(request, id):
    item = Order.objects.filter(id=id)
    if item.exists():
        item = item[0]
        context = {
        "items" : item
        }
        return render(request, 'invoice.html', context)



# @pdf_decorator
# def pdfView(request, id):
#     item = Order.objects.filter(id=id)
#     if item.exists():
#         item = item[0]
#         context = {
#         "item" : item
#         }
#         return render(request, 'invoice.html', context)

from instamojo_wrapper import Instamojo
API_KEY = "test_40664180402e64719e4ad001486"
AUTH_TOKEN = "test_4362430ec6fac7573e1048788af"
api = Instamojo(api_key=API_KEY,auth_token=AUTH_TOKEN,endpoint='https://test.instamojo.com/api/1.1/')


import razorpay
client = razorpay.Client(auth=("rzp_test_mp6FNCpzegnAZh", "rhclOvFrgFHEGSbK0YRwvXTN"))


TAX_VALUE_TYPES = (
    ('In Rupees', 'Rs'),
    ('In Percentage' , 'Percent')
)




@staff_member_required
def accept_order(request, id):
    marked = Order.objects.get(id=id)
    marked.order_placed = True
    marked.save()
    return redirect("core:adminOrders_View")

@staff_member_required
def decline_order(request, id):
    marked = Order.objects.get(id=id)
    marked.order_rejected = True
    marked.save()
    return redirect("core:adminOrders_View")

@staff_member_required
def delivered_order(request, id):
    marked = Order.objects.get(id=id)
    marked.being_delivered = True
    marked.save()
    return redirect("core:adminOrders_View")


def getOrders_Status(request):
    orders = Order.objects.filter(user=request.user, ordered=True)
    status = {"status":1}
    for order in orders:
        if order.order_placed == True and order.being_delivered ==True or order.order_rejected==True:
            pass
        else :
            status['status'] = 0

    print(status)
    return JsonResponse(status)


def ItemDetailsView(request, slug, value):
    item = Item.objects.filter(slug=slug)
    variation = FinalVariation.objects.filter(productId__slug=slug)
    data = {'has_data': 0}
    print(item, variation, value)
    if item.exists() and variation.exists():
        for item_var in variation:
            for var in item_var.variations.all():
                print(var.variationValue, var.variationValue.lower())
                if var.variationValue.lower() == value.lower():
                     data = {
                                'has_data': 1,
                                'id' : item_var.id,
                                'slug': item_var.variationName,
                                'price': float(item_var.price),
                            }
    print(data)
    return JsonResponse(data)

def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

def Register(request):
    categorys = Category.objects.filter(is_active=True)
    collections = Collection.objects.filter(is_active=True)
    context = {
            'category'  : categorys,
            'collection': collections
    }
    return render(request, 'register.html', context)

def Register_user(request):
    if request.method == 'POST':
        first_name = request.POST['fname']
        last_name = request.POST['lname']
        email = request.POST['email']
        contact_no = request.POST['phone']
        user_password = request.POST['password']
        confirm_password = request.POST['cpassword']
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email ID already taken.    Do Login If You Are An Existing User ")
            return  redirect('core:register_page')
        elif contact_no == "" or contact_no == " " or len(contact_no) < 1:
            messages.error(request, "Please Enter Your Contact Number.")
            return redirect('core:register_page')
        elif user_password != confirm_password:
            messages.error(request, "Entered Passwords are not same")
            return redirect('core:register_page')
        elif len(first_name)<1 and len(last_name) < 2:
            messages.error(request, "First Name and Last Name are too short")
            return redirect('core:register_page')
        else:
            user = User.objects.create_user(username=email, email=email,  password=user_password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            customer = Customer.objects.create(user=user, phoneNo=contact_no)
            customer.save()
            messages.success(request,"User is Registered Successfully")
            return redirect("core:login_view")

def login_view(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(username=email, password=password)
            if user is not None:
                login(request, user)
                if next is not None:
                    return redirect("core:home")
                else:
                    return redirect("core:home")
            else:
                messages.error(request, "Incorrect Login Details. If You are a new User do Register")
        categorys = Category.objects.filter(is_active=True)
        collections = Collection.objects.filter(is_active=True)
        context = {
            'category'  : categorys,
            'collection': collections
        }
        return render(request, 'login.html', context)
    else:
        return redirect("core:home")

def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect("core:home")

class ContactView(View):
    def get(self, *args, **kwargs):
        categorys = Category.objects.filter(is_active=True)
        collections = Collection.objects.filter(is_active=True)
        context = {
            'category'  : categorys,
            'collection': collections
        }
        return render(self.request, 'contac.html', context)

@login_required(login_url='core:login_view')
def add_to_cart(request, id, qt, value):
    item = FinalVariation.objects.get(id=id)
    # try:
    #     print("in var",slug)
    #     # item = get_object_or_404(FinalVariation, variationName=slug)
    #     try:
    #         item = FinalVariation.objects.get(variationName=slug)
    #     except:
    #         if int(value) != 0:
    #             for i in FinalVariation.objects.filter(variationName=slug):
    #                 for var in i.variations.all():
    #                     if var.variationValue == value:
    #                         item = i
    #                         break
    #         else:
    #             raise ValueError
    # except:
    #     print("in pri",slug)
    #     try:
    #         item = get_object_or_404(FinalVariation, productId__slug=slug)
    #     except:
    #         items = FinalVariation.objects.filter(variationName=slug)
    #         if items.exists():
    #             for i in FinalVariation.objects.filter(variationName=slug):
    #                 for var in i.variations.all():
    #                     if var.variationValue == None:
    #                         item = i
    #                         break
    print(item.id)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False,
        price=int(item.price)
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item=item, ordered=False).exists():
            order_item.quantity += int(qt)
            print("1--")
            order_item.save()
            if order.tax == None:
                order.tax = 0
            if order.totalPrice == None:
                order.totalPrice = 0
            order.tax = order.get_tax_amount()
            order.totalPrice = order.get_tax_include()
            order.save()
            messages.info(request, "Item qty was updated.")
            return redirect("core:order-summary")
        else:
            order_item.quantity = int(qt)
            print("2--")
            order_item.save()
            order.items.add(order_item)
            if order.tax == None:
                order.tax = 0
            if order.totalPrice == None:
                order.totalPrice = 0
            order.tax = order.get_tax_amount()
            order.totalPrice = order.get_tax_include()
            order.save()
            messages.info(request, "Item was added to your cart.")
            return redirect("core:order-summary")
    else:
        # add a message saying the Item was added to cart
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order_item.quantity = int(qt)
        order_item.save()
        order.items.add(order_item)
        order.save()#h6
        if order.tax == None:
            order.tax = 0
        if order.totalPrice == None:
            order.totalPrice = 0
        order.tax = order.get_tax_amount()
        order.totalPrice = order.get_tax_include()
        order.save()
        messages.info(request, "Item was added to your cart.")
    return redirect("core:order-summary")


@login_required(login_url='core:login_view')
def add_wish_to_cart(request, id):
    qt = 1
    orde = OrdeItem.objects.get(id=id)
    item = orde.item

    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False,
        price=int(item.price)
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__variationName=item.variationName, ordered=False).exists():
            order_item.quantity += int(qt)
            print("1--")
            order_item.save()
            if order.tax == None:
                order.tax = 0
            if order.totalPrice == None:
                order.totalPrice = 0
            order.tax = order.get_tax_amount()
            order.totalPrice = order.get_tax_include()
            order.save()
            messages.info(request, "Item qty was updated.")
            return redirect("core:order-summary")
        else:
            order_item.quantity = int(qt)
            print("2--")
            order_item.save()
            order.items.add(order_item)
            if order.tax == None:
                order.tax = 0
            if order.totalPrice == None:
                order.totalPrice = 0
            order.tax = order.get_tax_amount()
            order.totalPrice = order.get_tax_include()
            order.save()
            messages.info(request, "Item was added to your cart.")
            return redirect("core:order-summary")
    else:
        # add a message saying the Item was added to cart
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order_item.quantity = int(qt)
        order_item.save()
        order.items.add(order_item)
        order.save()#h6
        if order.tax == None:
            order.tax = 0
        if order.totalPrice == None:
            order.totalPrice = 0
        order.tax = order.get_tax_amount()
        order.totalPrice = order.get_tax_include()
        order.save()
        messages.info(request, "Item was added to your cart.")
    return redirect("core:order-summary")




@login_required(login_url='core:login_view')
def add_single_item(request, id, qt, value):
    # print("quantity", qt)
    # try:
    #     print("in var",slug)
    #     # item = get_object_or_404(FinalVariation, variationName=slug)
    #     try:
    #         item = FinalVariation.objects.get(variationName=slug)
    #     except:
    #         if int(value) != 0:
    #             for i in FinalVariation.objects.filter(variationName=slug):
    #                 for var in i.variations.all():
    #                     if var.variationValue == value:
    #                         item = i
    #                         break
    #         else:
    #             raise ValueError
    # except:
    #     print("in pri",slug)
    #     try:
    #         item = get_object_or_404(FinalVariation, productId__slug=slug)
    #     except:
    #         items = FinalVariation.objects.filter(variationName=slug)
    #         if items.exists():
    #             for i in FinalVariation.objects.filter(variationName=slug):
    #                 for var in i.variations.all():
    #                     if var.variationValue == None:
    #                         item = i
    #                         break
    item = FinalVariation.objects.get(id=id)
    print(item)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False,
        price=int(item.price)
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__variationName=item.variationName, ordered=False).exists():
            order_item.quantity += int(qt)
            print("1--")
            order_item.save()
            if order.tax == None:
                order.tax = 0
            if order.totalPrice == None:
                order.totalPrice = 0
            order.tax = order.get_tax_amount()
            order.totalPrice = order.get_tax_include()
            order.save()
            messages.info(request, "Item qty was updated.")
            return redirect("core:order-summary")
        else:
            order_item.quantity = int(qt)
            print("2--")
            order_item.save()
            order.items.add(order_item)
            if order.tax == None:
                order.tax = 0
            if order.totalPrice == None:
                order.totalPrice = 0
            order.tax = order.get_tax_amount()
            order.totalPrice = order.get_tax_include()
            order.save()
            messages.info(request, "Item was added to your cart.")
            return redirect("core:order-summary")
    else:
        # add a message saying the Item was added to cart
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order_item.quantity = int(qt)
        order_item.save()
        order.items.add(order_item)
        order.save()#h6
        if order.tax == None:
            order.tax = 0
        if order.totalPrice == None:
            order.totalPrice = 0
        order.tax = order.get_tax_amount()
        order.totalPrice = order.get_tax_include()
        order.save()
        messages.info(request, "Item was added to your cart.")
    return redirect("core:order-summary")


@login_required(login_url='core:login_view')
def add_pri_to_cart(request, slug, qt):
    print("error", slug)
    slug = slug.lower()
    item = get_object_or_404(Item, slug=slug)
    print("error")
    if item.discount_price:
        final_price = item.discount_price
        pre_finalvar = FinalVariation.objects.filter(productId=item, variationName=item.title, price=item.discount_price)
    else:
        pre_finalvar = FinalVariation.objects.filter(productId=item, variationName=item.title, price=item.price)
        final_price = item.price
    if pre_finalvar.exists():
        #print(pre_finalvar)
        finalvar = pre_finalvar[0]
    else:
        if item.discount_price:
            finalvar = FinalVariation.objects.create(productId=item, variationName=item.title, price=item.discount_price)
        else:
            finalvar = FinalVariation.objects.create(productId=item, variationName=item.title, price=item.price)
        finalvar.save()

    order_item, created = OrderItem.objects.get_or_create(
        item=finalvar,
        user=request.user,
        ordered=False,
        price=int(final_price)
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__variationName=finalvar.variationName,ordered=False).exists():
            order_item.quantity += int(qt)
            order_item.save()
            if order.tax == None:
                order.tax = 0
            if order.totalPrice == None:
                order.totalPrice = 0
            order.tax = order.get_tax_amount()
            order.totalPrice = order.get_tax_include()
            order.save()
            messages.info(request, "Item qty was updated.")
            return redirect("core:order-summary")
        else:
            order_item.quantity = int(qt)
            order_item.save()
            if order.tax == None:
                order.tax = 0
            if order.totalPrice == None:
                order.totalPrice = 0
            order.tax = order.get_tax_amount()
            order.totalPrice = order.get_tax_include()
            order.save()
            order.items.add(order_item)
            messages.info(request, "Item was added to your cart.")
            return redirect("core:order-summary")
    else:
        # add a message saying the Item was added to cart
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order_item.quantity = int(qt)
        order.items.add(order_item)
        if order.tax == None:
            order.tax = 0
        if order.totalPrice == None:
            order.totalPrice = 0
        order.tax = order.get_tax_amount()
        order.totalPrice = order.get_tax_include()
        order.save()
        messages.info(request, "Item was added to your cart.")
    return redirect("core:order-summary")

@login_required(login_url='core:login_view')
def clear_cart(request):
    order = Order.objects.filter(user=request.user, ordered=False)
    print(order)
    if order.exists():
        order = order[0]
        try:
            print("on")
            for item in order.items.all():
                item.delete()
            order.delete()
            print("on")
        except:
            pass
    return redirect("core:order-summary")



@login_required(login_url='core:login_view')
def remove_from_cart(request, id):
    # print(slug)
    # item = get_object_or_404(FinalVariation, variationName=slug)

    # try:
    #     print("in var",slug)
    #     # item = get_object_or_404(FinalVariation, variationName=slug)
    #     try:
    #         item = FinalVariation.objects.get(variationName=slug)
    #     except:
    #         if int(value) != 0:
    #             for i in FinalVariation.objects.filter(variationName=slug):
    #                 for var in i.variations.all():
    #                     if var.variationValue == value:
    #                         item = i
    #                         break
    #         else:
    #             raise ValueError  
    # except:
    #     print("in pri",slug)
    #     item = get_object_or_404(FinalVariation, productId__slug=slug)
    item = FinalVariation.objects.get(id=id)



    order_qs = Order.objects.filter(user=request.user, ordered=False )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        val = order.items.filter(item__variationName=item.variationName)
        if order.items.filter(item__variationName=item.variationName).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            if order.tax == None:
                order.tax = 0
            if order.totalPrice == None:
                order.totalPrice = 0
            order.tax = order.get_tax_amount()
            order.totalPrice = order.get_tax_include()
            order.save()
            messages.info(request, "Item was removed from your cart.")
            return redirect("core:order-summary")
        else:
            # add a message saying the user dosent have an order
            messages.info(request, "Item was not in your cart.")
            return redirect("core:product", slug=slug)
    else:
        # add a message saying the user dosent have an order
        messages.info(request, "u don't have an active order.")
        return redirect("core:product", slug=slug)
    return redirect("core:product", slug=slug)

@login_required(login_url='core:login_view')
@csrf_exempt
def post_form(request, slug, cat, val):
    print(request, slug, cat, val)
    item = get_object_or_404(Item, slug=slug)
    order_qs = MiddleVariation.objects.filter(productId=item, variationCategory=cat, variationValue = val)
    if order_qs.exists() == False:
        var = MiddleVariation.objects.create(productId=item, variationCategory=cat, variationValue = val)
        var.save()
        messages.info(request, "This variation was added.")
        return redirect("/#")
    else:
        messages.info(request, "This variation is already present")
        return redirect("/#")

@login_required(login_url='core:login_view')
def remove_single_item_from_cart(request, id, value):
    # item = get_object_or_404(FinalVariation, variationName=slug)
    # try:
    #     print("in var",slug)
    #     # item = get_object_or_404(FinalVariation, variationName=slug)
    #     try:
    #         item = FinalVariation.objects.get(variationName=slug)
    #     except:
    #         if int(value) != 0:
    #             for i in FinalVariation.objects.filter(variationName=slug):
    #                 for var in i.variations.all():
    #                     if var.variationValue == value:
    #                         item = i
    #                         break
    # except:
    #     print("in pri",slug)
    #     item = get_object_or_404(FinalVariation, productId__slug=slug)
    item = FinalVariation.objects.get(id=id)

    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__variationName=item.variationName).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
                if order.tax == None:
                    order.tax = 0
                if order.totalPrice == None:
                    order.totalPrice = 0
                order.tax = order.get_tax_amount()
                order.totalPrice = order.get_tax_include()
                order.save()
            else:
                order.items.remove(order_item)
                order_item.delete()
                if order.tax == None:
                    order.tax = 0
                if order.totalPrice == None:
                    order.totalPrice = 0
                order.tax = order.get_tax_amount()
                order.totalPrice = order.get_tax_include()
                order.save()
            messages.info(request, "This item qty was updated.")
            return redirect("core:order-summary")
        else:
            # add a message saying the user dosent have an order
            messages.info(request, "Item was not in your cart.")
            return redirect("core:product", slug=slug)
    else:
        # add a message saying the user dosent have an order
        messages.info(request, "u don't have an active order.")
        return redirect("core:product", slug=slug)
    return redirect("core:product", slug=slug)



@login_required(login_url='core:login_view')
def add_to_wish(request, slug, qt, value):
    # item = get_object_or_404(FinalVariation, variationName=slug)
    qt = 1
    try:
        print("in var",slug)
        # item = get_object_or_404(FinalVariation, variationName=slug)
        try:
            item = FinalVariation.objects.get(variationName=slug)
        except:
            if int(value) != 0:
                for i in FinalVariation.objects.filter(variationName=slug):
                    for var in i.variations.all():
                        if var.variationValue == value:
                            item = i
                            break
    except:
        print("in pri",slug)
        item = get_object_or_404(FinalVariation, productId__slug=slug)

    orde_item, created = OrdeItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordeed=False,
    )
    
    if created:
        orde_item.quantity = int(qt)
        messages.info(request, "Item was added to your wish.")
        return redirect("core:wish-summary")
    else:
        orde_item.quantity += int(qt)
        messages.info(request, "Item was added to your wish.")
    return redirect("core:wish-summary")

@login_required(login_url='core:login_view')
def add_pri_to_wish(request, slug, qt):
    item = get_object_or_404(Item, slug=slug)
    qt = 1
    if item.discount_price:
        final_price = item.discount_price
        pre_finalvar = FinalVariation.objects.filter(productId=item, variationName=item.title, price=item.discount_price)
    else:
        pre_finalvar = FinalVariation.objects.filter(productId=item, variationName=item.title, price=item.price)
        final_price = item.discount_price
    if pre_finalvar.exists():
        #print(pre_finalvar)
        finalvar = pre_finalvar[0]
    else:
        finalvar = FinalVariation.objects.create(productId=item, variationName=item.title, price=final_price)
        finalvar.save()
    # item = get_object_or_404(FinalVariation, variationName=slug)
    orde_item, created = OrdeItem.objects.get_or_create(
        item=finalvar,
        user=request.user,
        ordeed=False,
    )
    if created:
        orde_item.quantity = int(qt)
        messages.info(request, "Item was added to your wish.")
        return redirect("core:wish-summary")
    else:
        orde_item.quantity += int(qt)
        messages.info(request, "Item was added to your wish.")
    return redirect("core:wish-summary")




@login_required(login_url='core:login_view')
def remove_from_wish(request, slug, id):
    wish_item = OrdeItem.objects.filter(id=id)
    #print(wish_item)
    wish_item[0].delete()

    return redirect("core:wish-summary")

@login_required(login_url='core:login_view')
def clear_wish(request):
    wish_list = OrdeItem.objects.filter(user=request.user)
    if wish_list.exists():
        for wish in wish_list:
            wish.delete()
    return redirect("core:wish-summary")


@login_required(login_url='core:login_view')
def remove_single_item_from_wish(request, id, value):
    # # item = get_object_or_404(FinalVariation, variationName=slug)
    # try:
    #     print("in var",slug)
    #     # item = get_object_or_404(FinalVariation, variationName=slug)
    #     try:
    #         item = FinalVariation.objects.get(variationName=slug)
    #     except:
    #         if int(value) != 0:
    #             for i in FinalVariation.objects.filter(variationName=slug):
    #                 for var in i.variations.all():
    #                     if var.variationValue == value:
    #                         item = i
    #                         break
    # except:
    #     print("in pri",slug)
    #     item = get_object_or_404(FinalVariation, productId__slug=slug)
    item = FinalVariation.objects.get(id=id)
    order_qs = OrdeItem.objects.filter(
        user=request.user,
        ordeed=False,
        item=item
        )
    if order_qs.exists():
        order = order_qs[0]
    
        if order.quantity > 1:
            order.quantity -= 1
            order.save()
        else:
            order.delete()
        messages.info(request, "This item qty was updated.")
        return redirect("core:wish-summary")
    else:
        # add a message saying the user dosent have an order
        messages.info(request, "u don't have an active order.")
        return redirect("core:wish-summary", slug=slug)
    return redirect("core:wish-summary", slug=slug)



def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist")
        return redirect("core:checkout")


class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect("core:checkout")

            except ObjectDoesNotExist:
                messages.info(request, "You do not have an active order")
                return redirect("core:checkout")


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        categorys = Category.objects.filter(is_active=True)
        collections = Collection.objects.filter(is_active=True)
        context = {
            'form': form,
            'category' : categorys,
            'collection': collections
        }
        return render(self.request, "request_refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, "Your request was received")
                return redirect("core:request-refund")

            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exist")
                return redirect("core:request-refund")

class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = RadioCheckoutForm()
            categorys = Category.objects.filter(is_active=True)
            collections = Collection.objects.filter(is_active=True)
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True,
                'category' : categorys,
                'collection': collections
            }
            print(context)
            return render(self.request, "checkout.html", context)

        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        form = RadioCheckoutForm(self.request.POST or None)
        if form.is_valid():
            selected = form.cleaned_data.get("payment_option")
            print(selected)

        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            print(self.request.POST)
            print("in post checkout")
            if self.request.method == "POST":

                fname = self.request.POST.get('firstName')
                lname = self.request.POST.get('lastName')
                email = self.request.POST.get('email')
                number = self.request.POST.get("cnumber")
                street_address = self.request.POST.get('street_address')
                apartment_address = self.request.POST.get('apartment_address')
                address = self.request.POST.get('saddress1')#optional
                city = self.request.POST.get("City")
                state = self.request.POST.get("state")
                zip = self.request.POST.get('zip')

                try:
                    payment_option = self.request.POST.get('payment_option')
                    if payment_option == None or payment_option == "":
                        raise ValueError
                except:
                    return redirect("core:order-summary")

                billing_address = BillingAddress(
                    user=self.request.user,
                    fname=fname,
                    lname=lname,
                    email=email,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    address=address,
                    city=city,
                    state=state,
                    zip=zip,
                    address_type='B',
                    number=number
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()

                amount = int(order.totalPrice)
                purpose = str(order)
                user = User.objects.get(username=self.request.user)
                name = str(order)
                if payment_option == "InstaMojo":
                    response = api.payment_request_create(
                                amount=amount,
                                purpose=purpose,
                                buyer_name=user,
                                redirect_url="http://localhost:8000/"
                                )
                

                    if(response['success']):                    
                        messages.success(self.request, "Order was successful")
                        return redirect(response['payment_request']['longurl'])
                elif payment_option == "RazorPay":
                    razorpayResponse = client.order.create(dict(
                                        amount=amount*100,
                                        currency="INR",
                                        receipt=create_ref_code(),
                                        ))
                    order_id = razorpayResponse['id']
                    order_status = razorpayResponse['status']

                    if order_status=='created':

                        order = Order.objects.get(user=self.request.user, ordered=False)
                        form = CheckoutForm()
                        categorys = Category.objects.filter(is_active=True)
                        collections = Collection.objects.filter(is_active=True)
                        context = {
                            'form': form,
                            'couponform': CouponForm(),
                            'order': order,
                            'DISPLAY_COUPON_FORM': True,
                            'category' : categorys,
                            'collection': collections
                        }
                        context['order_id'] = order_id
                        context['price'] = amount
                        context['name'] = fname
                        context['phone'] = number
                        context['email'] = email
                        return render(self.request, "checkout.html", context)

                elif payment_option == "COD":
                    order = Order.objects.get(user=self.request.user, ordered=False)
                    payment = Payment()
                    payment.stripe_charge_id = "COD"
                    payment.user = self.request.user
                    payment.amount = order.get_total()
                    payment.save()

                    order.ordered = True
                    order.payment = payment
                    order.ref_code = create_ref_code()
                    order.save()
                    for i in order.items.all():
                        i.ordered = True
                        my_itm = Item.objects.get(id=i.item.productId.id)
                        my_itm.stock_no = int(my_itm.stock_no) - int(i.quantity)
                        my_itm.save()
                        i.save()

                    return redirect("core:orders")
                else:
                    return redirect("core:order-summary")

        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("core:order-summary")

class CategoryView(View):
    def get(self, *args, **kwargs):
        category = Category.objects.get(slug=self.kwargs['slug'])
        item = Item.objects.filter(category=category, is_active=True)
        context = {
            'object_list': item,
            'category_title': category,
            'category_description': category.description,
            'category_image': category.image
        }
        return render(self.request, "category.html", context)

class ItemDetailView(View):
    model = Item
    template_name = "singleproduct.html"
    def get(self, *args, **kwargs):
        pro = Item.objects.get(slug=kwargs['slug'])
        variation = FinalVariation.objects.filter(productId__slug=kwargs['slug'])
        var_list = []
        for i in variation:
            var_list.append(i)
        attribute = []
        temp = []
        attribute_val = {}

        #Getting the variations and passsing them to the website as dict
        for i in var_list:
            for j in i.variations.all():
                if j.variationCategory not in attribute:
                    attribute.append(j.variationCategory)
        for i in var_list:
            list_2 = []
            for j in i.variations.all():
                list_2.append(j.variationValue)
            temp.append(list_2)
        for i in attribute:
            attribute_val[i] = []
        for i in range(len(temp)):
            for j in range(len(temp[i])):
                if temp[i][j] not in attribute_val[attribute[j]]:
                    attribute_val[attribute[j]].append(temp[i][j])
        comment = Comment.objects.filter(product__slug=kwargs['slug'])
        print(pro, "-", attribute, "-", attribute_val, "-", var_list, "-", comment)
        att = []
        value = []
        var_name = []
        for var in variation:
            att.append(var.price)
            var_name.append(var.variationName)
            for item_var in var.variations.all():
                value.append(item_var.variationValue)
        print(att, "--", value)
        categorys = Category.objects.filter(is_active=True)
        collections = Collection.objects.filter(is_active=True)
        context = {
            'object':pro,
            'var_list' :attribute,#list
            'var_value':attribute_val,#dict
            'var'   :var_list,
            'slug'  :kwargs['slug'],
            'comments': comment,
            'final_att': att,
            'final_value': value,
            'final_name' : var_name,
            'category' : categorys,
            'collection': collections
        }
        print("CONTEXT ", context)
        return render(self.request, self.template_name, context)


class OrderSummaryView(LoginRequiredMixin, View):
    login_url = '/login'
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            #Passing The Variations to the website as dict
            attributes = {}
            for i in order.items.all():
                attributes[i.item.variationName] = []
                list_1 = {}
                for j in i.item.variations.all():
                    list_1[j.variationCategory] = j.variationValue
                attributes[i.item.variationName] = list_1
            categorys = Category.objects.filter(is_active=True)
            collections = Collection.objects.filter(is_active=True)
            context = {
                'object': order,
                'dict'  : attributes,
                'category' : categorys,
                'collection': collections
            }
            print(context)
            return render(self.request, 'cart.html', context)
        except ObjectDoesNotExist:
            categorys = Category.objects.filter(is_active=True)
            collections = Collection.objects.filter(is_active=True)
            context = {
                'object' : False,
                'category' : categorys,
                'collection': collections
            }
            messages.error(self.request, "You do not have an active order")
            return render(self.request, 'cart.html', context)


class HomeView(View):
    def get(self, *args, **kwargs):
        if self.request.GET.get('payment_id') and self.request.GET.get('payment_request_id'):
           
            payment_id = self.request.GET.get('payment_id') 
            payment_request_id =  self.request.GET.get('payment_request_id')
            secondResponse = api.payment_request_payment_status(payment_request_id, payment_id)
            
            print(secondResponse)
            if secondResponse['payment_request']['status'] == 'Completed' and secondResponse['payment_request']['payment']['failure'] == None and secondResponse['payment_request']['payment']['status'] == 'Credit':
               
                order = Order.objects.get(user=self.request.user, ordered=False)
                payment = Payment()
                payment.stripe_charge_id = secondResponse['payment_request']['id']
                payment.user = self.request.user
                payment.amount = order.get_total()
                payment.save()

                order.ordered = True
                order.payment = payment
                order.ref_code = create_ref_code()
                order.save()
                for i in order.items.all():
                    i.ordered = True
                    my_itm = Item.objects.get(id=i.item.productId.id)
                    my_itm.stock_no = int(my_itm.stock_no) - int(i.quantity)
                    my_itm.save()
                    i.save()

        query  = Item.objects.filter(is_active=True)
        slide = Slide.objects.filter(is_active=True)
        categorys = Category.objects.filter(is_active=True)
        collections = Collection.objects.filter(is_active=True)
        featuredProducts = Category.objects.get(slug="featured-products")
        featured = Item.objects.filter(is_active=True, category=featuredProducts)
        context = {
            'items' : query,
            'Slide' : slide,
            'category' : categorys,
            'collection': collections,
            'featuredProducts' : featured
        }
        return render(self.request, 'index.html', context)
    

def payment_status(request):
    if request.method == "POST":
        print("in post")
        print(request.POST)
        params_dict = {
            'razorpay_payment_id' : request.POST.get('razorpay_payment_id'),
            'razorpay_order_id' : request.POST.get('razorpay_order_id'),
            'razorpay_signature' : request.POST.get('razorpay_signature')
        }

        print(params_dict)
        # VERIFYING SIGNATURE
        try:
            print("in tyr")
            response = client.order.fetch(params_dict['razorpay_order_id'])
            # status = client.utility.verify_payment_signature(params_dict)
            print("status", response)
            if response['status'] == "paid" and response['amount_due'] == 0:
                order = Order.objects.get(user=request.user, ordered=False)
                payment = Payment()
                payment.stripe_charge_id = response['id']
                payment.user = request.user
                payment.amount = order.get_total()
                payment.save()

                order.ordered = True
                order.payment = payment
                order.ref_code = response['receipt']
                order.save()
                for i in order.items.all():
                    i.ordered = True
                    print("----------------------",i.item.productId.stock_no, i.quantity)
                    my_itm = Item.objects.get(id=i.item.productId.id)
                    my_itm.stock_no = int(my_itm.stock_no) - int(i.quantity)
                    my_itm.save()
                    i.save()
            return redirect("core:home")
        except:
            return redirect("core:home")
    else:
        print("out of  post")
# **********

class ShopView(ListView):
    model = Item
    paginate_by = 6
    template_name = "shop.html"


class WishView(LoginRequiredMixin, View):
    login_url = '/login'
    def get(self, *args, **kwargs):
        try:
            orde = OrdeItem.objects.filter(
                user=self.request.user, ordeed=False)
            categorys = Category.objects.filter(is_active=True)
            collections = Collection.objects.filter(is_active=True)
            context = {
                'object': orde,
                'category' : categorys,
                'collection': collections
            }
            return render(self.request, 'wish.html', context)
        except ObjectDoesNotExist:
            categorys = Category.objects.filter(is_active=True)
            collections = Collection.objects.filter(is_active=True)
            context = {
                'object': False,
                'category' : categorys,
                'collection': collections
            }
            messages.error(self.request, "wishlist is empty", context)
            return redirect("/")

class PaymentView(View):
    def get(self, *args, **kwargs):
        # order
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            context = {
                'order': order,
                'DISPLAY_COUPON_FORM': False
            }
            return render(self.request, "payment.html", context)
        else:
            messages.warning(
                self.request, "u have not added a billing address")
            return redirect("core:checkout")

def addcomment(request,id):
   url = request.META.get('HTTP_REFERER')  # get last url
   #return HttpResponse(url)
   if request.method == 'POST':  # check post
      form = CommentForm(request.POST)
      #print("in comment ", url, form)
      if form.is_valid():
         data = Comment()  # create relation with model
         data.subject = form.cleaned_data['subject']
         data.comment = form.cleaned_data['comment']
         data.rate = form.cleaned_data['rate']
         data.ip = request.META.get('REMOTE_ADDR')
         data.product_id=id
         current_user= request.user
         data.user_id=current_user.id
         data.save()  # save data to table
         messages.success(request, "Your review has ben sent. Thank you for your interest.")
         return HttpResponseRedirect(url)

   return HttpResponseRedirect(url)

def contactus(request):
    url = request.META.get('HTTP_REFERER') #get last url
    #print(url)
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            data = Contact()
            data.fname = form.cleaned_data['fname']
            data.lname = form.cleaned_data['lname']
            data.mobileno = form.cleaned_data['mobileno']
            data.emailId = form.cleaned_data['emailId']
            data.subject = form.cleaned_data['subject']
            current_user= request.user
            #print(current_user, current_user.id)
            if current_user.id:
                data.user_id=current_user.id
            else:
                data.user_id=None
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            return redirect('core:home')

        else:
            print("not valid")
    return HttpResponseRedirect(url)
# ***********




#Changed
#TODO change this to this view
@login_required(login_url='core:login_view')
def order_view(request):
    context = {}
    context["category"] = Category.objects.filter(is_active=True)
    context['collection'] = Collection.objects.filter(is_active=True)
    user = request.user
    if Order.objects.filter(user=user).exists():
        cart_items = reversed(Order.objects.filter(user=user, ordered=True))
        cart_items_list = []
        for i in cart_items:
            cart_items_list.append(i)
        context['items'] = cart_items_list

        list_1 = []
        for item in cart_items_list:
            if item.order_rejected == True or item.being_delivered == True:
                list_1.append(True)
            else:
                list_1.append(False)
        context["status"] = list_1
        context["category"] = Category.objects.filter(is_active=True)
        context['collection'] = Collection.objects.filter(is_active=True)
        return render(request,'myorder.html', context)
    else:
        return render(request, 'myorder.html', context)

@staff_member_required
def adminOrders_View(request):
    context = {}
    # orders = reversed(OrdersPlaced.objects.filter(order_placed=False, order_rejected=False))
    # time_range = timezone.now() - timedelta(hours=24)
    orders = Order.objects.filter(ordered=True).order_by('-id')
    orders_list = []
    for i in orders:
        print(i.id)
        orders_list.append(i)
    
    paginator = Paginator(orders_list, 10)
    page_number = request.GET.get('page')
    if not page_number:
        page_number=1
    page_obj = paginator.get_page(page_number)
    print("in page" , page_obj)
    context['orders'] = page_obj

    totalOrders=ordersPending=ordersAccepted=ordersCancelled=ordersDelivered=0
    for order in orders:
        totalOrders+=1
        if order.order_placed==False and order.order_rejected==False:
            ordersPending+=1
        if order.order_placed==True and order.being_delivered==False:
            ordersAccepted+=1
        if order.order_rejected==True:
            ordersCancelled+=1
        if order.order_placed==True and order.being_delivered==True:
            ordersDelivered+=1
    context['ordersPending'] = ordersPending
    context['ordersAccepted'] = ordersAccepted
    context['ordersCancelled'] = ordersCancelled
    context['ordersDelivered'] = ordersDelivered
    context['totalOrders'] = totalOrders
    context["category"] = Category.objects.filter(is_active=True)
    context['collection'] = Collection.objects.filter(is_active=True)
    return render(request, 'adminmyorders.html', context)


# @login_required(login_url='core:login_view')
def menu_view(request, num):
    if num == 0 or num == '0':
        context = {"items":  Item.objects.filter(is_active=True)}
        context['is_all']  = True
        context['title'] = "All Products"
    else:
        context = {"items":  Item.objects.filter(is_active=True, category__title=num)}
        context['is_all']  = False
        context['title'] = num
    # categorys = Category.objects.filter(is_active=True)
    # collections = Collections.objects.filter(is_active=True)
    context['category'] = Category.objects.filter(is_active=True)
    context['collection'] = Collection.objects.filter(is_active=True)
    context['is_category'] = True
    context['is_collection'] = False
    print("IN context", context)
    return render(request, 'product.html', context)

def menu_view_collections(request, num):
    if num == 0 or num == '0':
        context = {"items":  Item.objects.filter(is_active=True)}
        context['is_all']  = True
        context['title'] = "All Products"
    else:
        context = {"items":  Item.objects.filter(is_active=True, collection__title=num)}
        context['is_all']  = False
        context['title'] = num
    context['category'] = Category.objects.filter(is_active=True)
    context['collection'] = Collection.objects.filter(is_active=True)
    context['is_category'] = False
    context['is_collection'] = True
    print("IN context", context)
    return render(request, 'product.html', context)


