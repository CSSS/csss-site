from django.shortcuts import render
import os
from django.http import HttpResponseRedirect
from .models import Merchandise, Order, Option, OptionChoice, SelectedOrderMerchandise, SelectedOrderMerchandiseOptionChoice, Customer
from django.core import serializers
import datetime
from django.conf import settings
import stripe
import time as time_lib
# Create your views here.

stripe.api_key = settings.STRIPE_SECRET_KEY

def convert_session_to_list(request):
    print("[shopping/views.py convert_session_to_list()]")
    selected_merchandise=[]
    if 'data' in request.session:
        data=request.session['data']
        order = None
        order_item = None
        merch = None
        opt = None
        ch = None
        for obj in serializers.deserialize("xml", data):
            if hasattr(obj.object, 'order_id'):
                order = Order(
                    order_id = obj.object.order_id,
                    date = obj.object.date,
                    time = obj.object.time
                )
                selected_merchandise.append(order)
            if hasattr(obj.object, 'choice'):
                ch = OptionChoice(
                    optionChoice_option_key = opt,
                    choice = obj.object.choice
                )
                selected_merchandise.append(ch)
            elif hasattr(obj.object, 'merchandise'):
                merch = Merchandise(
                    merchandise = obj.object.merchandise,
                    image = obj.object.image,
                    price = obj.object.price
                )
                selected_merchandise.append(merch)
            elif hasattr(obj.object, 'option'):
                opt = Option(
                    option_merchandise_key = merch,
                    option = obj.object.option
                )
                selected_merchandise.append(opt)
            elif hasattr(obj.object, 'quantity'):
                odr_item = SelectedOrderMerchandise(
                    orderItem_order_key = order,
                    orderItem_merchandise_key = merch,
                    quantity = obj.object.quantity
                )
                selected_merchandise.append(odr_item)
    print("[shopping/views.py convert_session_to_list()] returning the list")
    return selected_merchandise

def convert_merchandse_list_to_session(listOfOptions, request):
    print("[shopping/views.py convert_merchandse_list_to_session()]")
    data = serializers.serialize("xml", listOfOptions)
    request.session['data']=data
    print("[shopping/views.py convert_merchandse_list_to_session()] data serialized and saved to request.session[data]")

def clearCart(request):
    print(f"[shopping/views.py clearCart()]")
    keys_to_clear = [key for key in request.session.keys() if '_auth_user_' not in key]
    for key in keys_to_clear:
        print(f"[shopping/views.py clearCart()] clearing entry under request.session[{key}]")
        del request.session[key]

def print_catalogue(request):
    print(f"[shopping/views.py print_catalogue()]")
    if 'clear' in request.POST:
        print(f"[shopping/views.py print_catalogue()] clear detected in request.POST")
        clearCart(request)
        return HttpResponseRedirect('/shopping')

    object_list = Merchandise.objects.all()

    context = {
        'tab': 'shopping',
        'object_list': object_list,
    }
    return render(request, 'shopping/catalogue.html', context)

def add_item_to_cart(request):
    print(f"[shopping/views.py add_item_to_cart()]")
    if not('merchandise' in request.POST and 'Color' in request.POST and 'Size' in request.POST and 'Quantity' in request.POST):
        print("[shopping/views.py add_item_to_cart()] not all keys necessary for adding item to cart are specified")
        return HttpResponseRedirect('/shopping')

    if 'merchandise' in request.POST and 'Color' in request.POST and 'Size' in request.POST and 'Quantity' in request.POST:
        print("[shopping/views.py add_item_to_cart()] correct keys detected in request.POST for adding to cart")
        merchandise_on_cart=convert_session_to_list(request)
        if len(merchandise_on_cart) > 0 and not hasattr(merchandise_on_cart[0], 'order_id'):
            print("[shopping/views.py add_item_to_cart()] incorrectly configured merchandise_on_cart detected, resetting to 0")
            merchandise_on_cart = []
        if len(merchandise_on_cart) == 0:
            print("[shopping/views.py add_item_to_cart()] initializing merchandise_on_cart with an order entry")
            now = datetime.datetime.now()
            date = datetime.date(now.year, now.month, now.day)
            time = now.time()
            ts = int(time_lib.time())
            order_id = str(request.COOKIES['sessionid']) + str(ts)
            order = Order(
                order_id = order_id,
                date = date,
                time = time
            )
            merchandise_on_cart.append(order)

        merchandise_selected=[]

        merch = Merchandise.objects.get(
            merchandise = request.POST['merchandise']
        )

        merchandise_selected.append(merch)

        for key in request.POST.keys():
            if key != 'merchandise' and key != 'csrfmiddlewaretoken' and key != 'Quantity':
                print(f"[shopping/views.py add_item_to_cart()] processing key {key} and value {request.POST[key]} for merchandise selected")
                opt = Option.objects.get(
                    option_merchandise_key = merch,
                    option = key
                )
                merchandise_selected.append(opt)
                ch = OptionChoice.objects.get(
                    optionChoice_option_key = opt,
                    choice = request.POST[key]
                )
                merchandise_selected.append(ch)

        itemQuantity = SelectedOrderMerchandise(
            orderItem_order_key = merchandise_on_cart[0],
            orderItem_merchandise_key = merch,
            quantity = int(request.POST['Quantity'])
        )

        merchandise_selected.append(itemQuantity)

        merchandiseFound = False
        index = 0
        while index < len(merchandise_on_cart):
            if index > 0 and not merchandiseFound:
                if hasattr(merchandise_on_cart[index], 'merchandise'):
                    if merchandise_selected[0].merchandise == merchandise_on_cart[index].merchandise \
                            and merchandise_selected[1].option == merchandise_on_cart[index+1].option \
                            and merchandise_selected[2].choice == merchandise_on_cart[index+2].choice \
                            and merchandise_selected[3].option == merchandise_on_cart[index+3].option \
                            and merchandise_selected[4].choice == merchandise_on_cart[index+4].choice:
                                merchandiseFound = True
                                old_quantity = merchandise_on_cart[index+5].quantity
                                new_quantity = merchandise_on_cart[index+5].quantity + int(request.POST['Quantity'])
                                print(f"[shopping/views.py add_item_to_cart()] updating quantity from {old_quantity} to {new_quantity} for { merchandise_selected[0].merchandise}")
                                merchandise_on_cart[index+5].quantity = new_quantity
                                index = index + 5
                    else:
                        index = index + 1
                else:
                    index = index + 1
            else:
                index = index + 1

        if not merchandiseFound:
            print(f"[shopping/views.py add_item_to_cart()] {merchandise_selected[0].merchandise} not found in the cart")
            merchandise_on_cart.append(merchandise_selected[0])
            merchandise_on_cart.append(merchandise_selected[1])
            merchandise_on_cart.append(merchandise_selected[2])
            merchandise_on_cart.append(merchandise_selected[3])
            merchandise_on_cart.append(merchandise_selected[4])
            merchandise_on_cart.append(merchandise_selected[5])

        convert_merchandse_list_to_session(merchandise_on_cart, request)
    return HttpResponseRedirect('/shopping')

def get_order_total_from_cache(merchandise_selected):
    print(f"[shopping/views.py get_order_total_from_cache()]")
    price = 0
    item_total = 0
    for indx, item in enumerate(merchandise_selected):
        if indx > 0:
            if hasattr(merchandise_selected[indx], 'price'):
                price = merchandise_selected[indx].price
            if hasattr(merchandise_selected[indx], 'quantity'):
                item_total = item_total + (price * merchandise_selected[indx].quantity)
    print(f"[shopping/views.py get_order_total_from_cache()] price calculated = {item_total}")
    return int(item_total)

def checkout_page(request):
    print(f"[shopping/views.py checkout_page()]")

    listOfOptions=convert_session_to_list(request)

    merchandise_selected = []
    index = 0
    while index < len(listOfOptions):
            if index > 0:
                current_item = []
                current_item.append(listOfOptions[index].image)
                current_item.append(listOfOptions[index].merchandise)
                current_item.append(listOfOptions[index].price)
                current_item.append(listOfOptions[index+2].choice)
                current_item.append(listOfOptions[index+4].choice)
                current_item.append(listOfOptions[index+5].quantity)
                index = index + 6
                merchandise_selected.append(current_item)
            else:
                index = index + 1
    if index == 0:
        context = {
            'tab': 'shopping',
            'object_selected': None,
        }
        print(f"[shopping/views.py checkout_page()] no items detected in cart")
    else:
        context = {
            'tab': 'shopping',
            'object_selected': merchandise_selected,
            'total': get_order_total_from_cache(listOfOptions)
        }
        print(f"[shopping/views.py checkout_page()] items detected and will be displayed")

    return render(request, 'shopping/checkout.html', context)


def update_merchandise_on_cart(merchandise, size, color, quantity, merchandise_on_cart):
    print(f"[shopping/views.py update_merchandise_on_cart()] searching for {merchandise} {size} {color}")
    index = 0
    while index < len(merchandise_on_cart):
        if hasattr(merchandise_on_cart[index], 'merchandise'):
            if merchandise_on_cart[index].merchandise == merchandise \
                and merchandise_on_cart[index+1].option == 'Size' \
                and merchandise_on_cart[index+2].choice == size \
                and merchandise_on_cart[index+3].option == 'Color' \
                and merchandise_on_cart[index+4].choice == color:
                    print(f"[shopping.views update_merchandise_on_cart()] quantity updated to {quantity} for {merchandise} {size} {color}")
                    merchandise_on_cart[index+5].quantity = quantity
                    return
        index = index + 1


def update_cart(request):
    print("[shopping/views.py update_cart()]")
    merchandise_on_cart=convert_session_to_list(request)
    for indx, value in enumerate(request.POST.getlist('merchandise')):
        merchandise = value
        size = request.POST.getlist('size')[indx]
        color = request.POST.getlist('color')[indx]
        quantity = request.POST.getlist('Quantity')[indx]
        print(f"[shopping/views.py update_cart()] updating {size}, {color} and {quantity} for merchandise {merchandise}")
        update_merchandise_on_cart(merchandise, size, color, quantity, merchandise_on_cart)
    convert_merchandse_list_to_session(merchandise_on_cart, request)
    return HttpResponseRedirect('/shopping/checkout')

def get_order_total(order_id):
    print("[shopping/views.py get_order_total()]")
    order = Order.objects.get(order_id=order_id)
    item_total = 0
    for item_ordered in SelectedOrderMerchandise.objects.all().filter(orderItem_order_key=order):
        item_total = item_total + ( 100 * ( item_ordered.quantity * item_ordered.orderItem_merchandise_key.price ) )
    print(f"[shopping/views.py get_order_total()] price calculated = {item_total}")
    return int(item_total)

def purchase(request):
    print(f"[shopping/views.py purchase()] request.session['data']={request.session['data']}")
    existing_order=convert_session_to_list(request)
    order = None
    merch = None
    quantity = None
    merchandise_for_order = None
    opt = None

    customer = Customer(
        name = request.POST['full_name'],
        sfu_email = request.POST['sfu_email']
    )
    customer.save()
    for indx, item in enumerate(existing_order):
        if indx == 0:
            order = item
            order.order_customer_key = customer
            order.save()
            print("[shopping/views.py purchase()] order saved")
        elif hasattr(item, 'merchandise'):
            merch = Merchandise.objects.get(merchandise=item.merchandise)
            merchandise_for_order = SelectedOrderMerchandise(
                orderItem_order_key = order,
                orderItem_merchandise_key = merch
            )
            merchandise_for_order.save()
            print("[shopping/views.py purchase()] SelectedOrderMerchandise saved")
        elif hasattr(item, 'option'):
            print(f"[shopping/views.py purchase()] encountered option {item.option}")
            opt = Option.objects.get(
                option = item.option,
                option_merchandise_key = merch
            )
        elif hasattr(item, 'choice'):
            ch = OptionChoice.objects.get(
                choice = item.choice,
                optionChoice_option_key = opt
            )
            optSelect = SelectedOrderMerchandiseOptionChoice(
                OrderOptionChoiceSelected_orderItem_key = merchandise_for_order,
                OrderOptionChoiceSelected_option_key = opt,
                OrderOptionChoiceSelected_optionChoice_key = ch
            )
            optSelect.save()
            print("[shopping/views.py purchase()] optSelect saved")
        elif hasattr(item, 'quantity'):
            merchandise_for_order.quantity = item.quantity
            merchandise_for_order.save()
            print("[shopping/views.py purchase()] merchandise_for_order saved")

    amount = get_order_total(order.order_id)
    publishKey = settings.STRIPE_PUBLISHABLE_KEY
    if request.method == 'POST':
        token = request.POST.get('stripeToken', False)
        if token:
            try:
                charge = stripe.Charge.create(
                    amount=amount,
                    currency='cad',
                    description='CSSS Merchandise',
                    source=token,
                )
                print(f"[shopping/views.py purchase()] order has been placed for {amount}")
                request.session['data']=''
                return HttpResponseRedirect('/shopping/checkout_form')
            except Exception as e:
                print(f"[shopping/views.py purchase()] Following Exception encountered\n{e}")
        else:
            print(f"[shopping/views.py purchase()] no token detecteds")

    context = {
        'order': existing_order,
        'STRIPE_PUBLISHABLE_KEY': publishKey
    }
    return render(request, 'shopping/print_catalogue.html', context)


def remove_item_from_cart(request):
    print("[shopping/views.py remove_item_from_cart()] ")
    merchandise_on_cart=convert_session_to_list(request)
    new_merchandise_list = []
    token = request.POST['action']
    firstIndex = token.index("_")
    secondIndex = token.index("_", firstIndex+1)
    merchandise = token[firstIndex+1:secondIndex]
    thirdIndex = token.index("_", secondIndex+1)
    size = token[secondIndex+1:thirdIndex]
    color = token[thirdIndex+1:]

    index = 0
    print(f"[shopping/views.py remove_item_from_cart()] searching for {merchandise} {size} {color}")
    while index < len(merchandise_on_cart):
        if hasattr(merchandise_on_cart[index], 'merchandise'):
            if merchandise_on_cart[index].merchandise == merchandise \
                and merchandise_on_cart[index+1].option == 'Size' \
                and merchandise_on_cart[index+2].choice == size \
                and merchandise_on_cart[index+3].option == 'Color' \
                and merchandise_on_cart[index+4].choice == color:
                index = index + 6
                print(f"[shopping/views.py remove_item_from_cart()] skipping over an item")
            else:
                print(f"[shopping/views.py remove_item_from_cart()] 1-adding {merchandise_on_cart[index]} to the list")
                new_merchandise_list.append(merchandise_on_cart[index])
                index = index + 1
        else:
            print(f"[shopping/views.py remove_item_from_cart()] 2-adding {merchandise_on_cart[index]} to the list")
            new_merchandise_list.append(merchandise_on_cart[index])
            index = index + 1
    convert_merchandse_list_to_session(new_merchandise_list, request)
    return HttpResponseRedirect('/shopping/checkout')

def checkout_form(request):
    print(f"[shopping/views.py checkout_form()]")
    if 'action' in request.POST and request.POST['action'] == 'update_cart':
        return update_cart(request)
    elif 'stripeToken' in request.POST:
        return purchase(request)
    elif 'action' in request.POST and 'remove' in request.POST['action']:
        return remove_item_from_cart(request)
    if 'clear' in request.POST:
        clearCart(request)
    return checkout_page(request)
