from django.shortcuts import render
import os
from django.http import HttpResponseRedirect
from .models import Merchandise, Order, Option, OptionChoice, OrderItem, OptionChoiceSelected
from django.core import serializers
import datetime
from django.conf import settings
import stripe
# Create your views here.

stripe.api_key = "sk_test_BAsVtUiIpXqNgjHBiOpGCAyr"

def back_to_list_of_merchandise(request):
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
                    name = obj.object.name,
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
                odr_item = OrderItem(
                    orderItem_order_key = order,
                    orderItem_merchandise_key = merch,
                    quantity = obj.object.quantity
                )
                selected_merchandise.append(odr_item)
    return selected_merchandise

def convert_merchandse_list_to_session(listOfOptions, request):
    data = serializers.serialize("xml", listOfOptions)
    request.session['data']=data

def catalogue(request):
    print("\n\tcatalogue")
    if 'clear' in request.POST:
        keys_to_clear = [key for key in request.session.keys() if '_auth_user_' not in key]
        print(f"keys_to_clear={keys_to_clear}")
        for key in keys_to_clear:
            print(f"clearing key {key}")
            del request.session[key]
        return HttpResponseRedirect('/shopping')

    print(f"request.POST={request.POST}")
    print(f"request.COOKIES={request.COOKIES}")

    for key in request.session.keys():
        print("request.session["+str(key)+"]="+str(request.session[key]))
        object_list = Merchandise.objects.all()
    # Set your secret key: remember to change this to your live secret key in production
    # See your keys here: https://dashboard.stripe.com/account/apikeys
    context = {
        'tab': 'shopping',
        'object_list': object_list,
    }
    print("the end")
    return render(request, 'shopping/catalogue.html', context)

def add_item_to_cart(request):
    if not('merchandise' in request.POST and 'Color' in request.POST and 'Size' in request.POST and 'Quantity' in request.POST):
        print("[views.py add_item_to_cart] not all keys necessary for adding item to cart are specified")
        return HttpResponseRedirect('/shopping')

    if 'merchandise' in request.POST and 'Color' in request.POST and 'Size' in request.POST and 'Quantity' in request.POST:
        print("****PROCESSING TRANSACTION****")
        print(f"request.POST={request.POST}")
        merchandise_on_cart=back_to_list_of_merchandise(request)
        if len(merchandise_on_cart) > 0 and not hasattr(merchandise_on_cart[0], 'order_id'):
            # print("incorrectly configured merchandise_on_cart detected, resetting to 0")
            merchandise_on_cart = []
        if len(merchandise_on_cart) == 0:
            # print("initializing merchandise_on_cart with an order entry")
            now = datetime.datetime.now()
            date = datetime.date(now.year, now.month, now.day)
            time = now.time()
            order = Order(
                order_id = request.COOKIES['sessionid'],
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
            # print(f"\n\tkey encountered={key}\n\tvalue={request.POST[key]}")
            if key != 'merchandise' and key != 'csrfmiddlewaretoken' and key != 'Quantity':
                print(f"\n\tkey being processed={key}\n\tvalue={request.POST[key]}")
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

        itemQuantity = OrderItem(
            orderItem_order_key = merchandise_on_cart[0],
            orderItem_merchandise_key = merch,
            quantity = int(request.POST['Quantity'])
        )

        merchandise_selected.append(itemQuantity)
        #for indx, val in enumerate(merchandise_selected):
        #    print(f"\n\tkey that were processed={val} with index {indx}")

        merchandiseFound = False
        index = 0
        while index < len(merchandise_on_cart):
            print(f"1")
            obj = merchandise_on_cart[index]
            if index > 0 and not merchandiseFound:
                print(f"3")
                if hasattr(merchandise_on_cart[index], 'merchandise'):
                    print(f"3")
                    if merchandise_selected[0].merchandise == merchandise_on_cart[index].merchandise \
                            and merchandise_selected[1].option == merchandise_on_cart[index+1].option \
                            and merchandise_selected[2].choice == merchandise_on_cart[index+2].choice \
                            and merchandise_selected[3].option == merchandise_on_cart[index+3].option \
                            and merchandise_selected[4].choice == merchandise_on_cart[index+4].choice:
                                merchandiseFound = True
                                merchandise_on_cart[index+5].quantity = merchandise_on_cart[index+5].quantity + int(request.POST['Quantity'])
                                index = index + 5
                    else:
                        index = index + 1
                else:
                    index = index + 1
            else:
                index = index + 1

        if not merchandiseFound:
            print("new merchandise being added to the cart")
            merchandise_on_cart.append(merchandise_selected[0])
            merchandise_on_cart.append(merchandise_selected[1])
            merchandise_on_cart.append(merchandise_selected[2])
            merchandise_on_cart.append(merchandise_selected[3])
            merchandise_on_cart.append(merchandise_selected[4])
            merchandise_on_cart.append(merchandise_selected[5])

        convert_merchandse_list_to_session(merchandise_on_cart, request)
    return HttpResponseRedirect('/shopping')

def get_order_total_seralized(merchandise_selected):
    index = 0
    price = 0
    item_total = 0
    while index < len(merchandise_selected):
        if index > 0:
            if hasattr(merchandise_selected[index], 'price'):
                price = merchandise_selected[index].price
            if hasattr(merchandise_selected[index], 'quantity'):
                item_total = item_total + (price * merchandise_selected[index].quantity)
        index = index + 1

    return int(item_total)

def checkout_1(request):
    print("checkout")
    print(f"request.POST={request.POST}")
    # Set your secret key: remember to change this to your live secret key in production
    # See your keys here: https://dashboard.stripe.com/account/apikeys

    listOfOptions=back_to_list_of_merchandise(request)

    merchandise_selected = []
    index = 0
    while index < len(listOfOptions):
            if index > 0:
                merchandise_ = []
                merchandise_.append(listOfOptions[index].image)
                merchandise_.append(listOfOptions[index].merchandise)
                merchandise_.append(listOfOptions[index].price)
                merchandise_.append(listOfOptions[index+2].choice)
                merchandise_.append(listOfOptions[index+4].choice)
                merchandise_.append(listOfOptions[index+5].quantity)
                index = index + 6
                merchandise_selected.append(merchandise_)
            else:
                index = index + 1
    context = {
        'tab': 'shopping',
        'object_selected': merchandise_selected,
        'total': get_order_total_seralized(listOfOptions)
    }

    return render(request, 'shopping/checkout.html', context)


def update_merchandise_on_cart(merchandise, size, color, quantity, merchandise_on_cart):
    print(f"[shopping.views update_merchandise_on_cart()] searching for {merchandise} {size} {color}")
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
    print("[shopping.views update_cart()] ")
    merchandise_on_cart=back_to_list_of_merchandise(request)
    index = 0
    while index < len(request.POST.getlist('merchandise')):
        merchandise = request.POST.getlist('merchandise')[index]
        size = request.POST.getlist('size')[index]
        color = request.POST.getlist('color')[index]
        quantity = request.POST.getlist('Quantity')[index]
        update_merchandise_on_cart(merchandise, size, color, quantity, merchandise_on_cart)
        index = index + 1
    convert_merchandse_list_to_session(merchandise_on_cart, request)
    return HttpResponseRedirect('/shopping/checkout')

def get_order_total(order_id):
    order = Order.objects.get(order_id=order_id)
    item_total = 0
    for item_ordered in OrderItem.objects.all().filter(orderItem_order_key=order):
        item_total = item_total + ( 100 * ( item_ordered.quantity * item_ordered.orderItem_merchandise_key.price ) )

    return int(item_total)

def purchase(request):
    print(f"[shopping.views purchase()]")
    existing_order=back_to_list_of_merchandise(request)
    order = None
    merch = None
    quantity = None
    orderItem = None
    for indx, item in enumerate(existing_order):
        if indx == 0:
            order = item
            order.save()
        elif hasattr(item, 'merchandise'):
            merch = Merchandise.objects.get(merchandise=item.merchandise)
            orderItem = OrderItem(
                orderItem_order_key = order,
                orderItem_merchandise_key = merch
            )
            orderItem.save()
        elif hasattr(item, 'option'):
            print(f"item with option is {item}")
            opt = Option.objects.get(
                option = item.option,
                option_merchandise_key = merch
            )
        elif hasattr(item, 'choice'):
            ch = OptionChoice.objects.get(
                choice = item.choice,
                optionChoice_option_key = opt
            )
            optSelect = OptionChoiceSelected(
                optionChoiceSelected_orderItem_key = orderItem,
                optionChoiceSelected_option_key = opt,
                optionChoiceSelected_optionChoice_key = ch
            )
            optSelect.save()
        elif hasattr(item, 'quantity'):
            orderItem.quantity = item.quantity
            orderItem.save()

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
                print(f"[shopping.views purchase()] 4")
                request.session['data']=''
                return HttpResponseRedirect('/shopping/checkout_form')
            except Exception as e:
                print(f"[shopping.views purchase()] 5")
                print(f"Your card has experienced following error.{e}")
        else:
            print(f"[shopping.views purchase()] 6")
            print("no token detecteds")

    context = {
        'order': existing_order,
        'STRIPE_PUBLISHABLE_KEY': publishKey
    }
    print(f"[shopping.views purchase()] 7")
    return render(request, 'shopping/catalogue.html', context)


def remove_item_from_cart(request):
    print("[shopping.views remove_item_from_cart()] ")
    merchandise_on_cart=back_to_list_of_merchandise(request)
    new_merchandise_list = []
    token = request.POST['action']
    firstIndex = token.index("_")
    secondIndex = token.index("_", firstIndex+1)
    merchandise = token[firstIndex+1:secondIndex]
    thirdIndex = token.index("_", secondIndex+1)
    size = token[secondIndex+1:thirdIndex]
    color = token[thirdIndex+1:]

    index = 0
    print(f"[shopping.views remove_item_from_cart()] searching for {merchandise} {size} {color}")
    while index < len(merchandise_on_cart):
        if hasattr(merchandise_on_cart[index], 'merchandise'):
            if merchandise_on_cart[index].merchandise == merchandise \
                and merchandise_on_cart[index+1].option == 'Size' \
                and merchandise_on_cart[index+2].choice == size \
                and merchandise_on_cart[index+3].option == 'Color' \
                and merchandise_on_cart[index+4].choice == color:
                index = index + 6
                print(f"[shopping.views remove_item_from_cart()] skipping over an item")
            else:
                print(f"[shopping.views remove_item_from_cart()] 1-adding {merchandise_on_cart[index]} to the list")
                new_merchandise_list.append(merchandise_on_cart[index])
                index = index + 1
        else:
            print(f"[shopping.views remove_item_from_cart()] 2-adding {merchandise_on_cart[index]} to the list")
            new_merchandise_list.append(merchandise_on_cart[index])
            index = index + 1
    convert_merchandse_list_to_session(new_merchandise_list, request)
    return HttpResponseRedirect('/shopping/checkout')

def checkout_form(request):
    print(f"[shopping.views checkout_form()] request.POST={request.POST}")
    if 'action' in request.POST and request.POST['action'] == 'update_cart':
        return update_cart(request)
    elif 'stripeToken' in request.POST:
        return purchase(request)
    elif 'action' in request.POST and 'remove' in request.POST['action']:
        return remove_item_from_cart(request)
    print("[shopping.views checkout_form()]  nothing detected")
    return checkout_1(request)
