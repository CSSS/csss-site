from django.shortcuts import render
import os
from django.http import HttpResponseRedirect
from .models import Merchandise, Order, Feature, Specification, OrderItem, OrderItemSpecification, Customer
from django.core import serializers
import datetime
from django.conf import settings
import stripe
import time as time_lib
import xml.etree.ElementTree as ET

# Create your views here.

stripe.api_key = settings.STRIPE_SECRET_KEY

def convert_session_to_list(request):
    print("[shopping/views.py convert_session_to_list()]")
    selected_merchandise=[]
    if 'data' in request.session:
        data=request.session['data']
        # print(f"data={data}")
        root = ET.fromstring(data)
        for object in root:
            if 'model' in object.attrib:
                if object.attrib['model'] == 'shopping.order':
                    for childObject in object:
                        if childObject.attrib['name'] == 'date':
                            date = childObject.text[:]
                            date = datetime.datetime.strptime(date[:10], '%Y-%m-%d')
                        elif childObject.attrib['name'] == 'time':
                            time = childObject.text
                            if len(time) > len('23:53:09.324139'):
                                time = time[11:]
                            time = datetime.datetime.strptime(time, '%H:%M:%S.%f')
                    order = Order(
                        order_id = object.attrib['pk'],
                        date = date,
                        time = time
                    )

                    selected_merchandise.append(order)
                elif object.attrib['model'] == 'shopping.specification':
                    for childObject in object:
                        if childObject.attrib['name'] == 'specification_type':
                            detectedSpec = childObject.text
                    spec = Specification(
                        feature_key = feature,
                        specification_type = detectedSpec,
                    )
                    selected_merchandise.append(spec)
                elif object.attrib['model'] == 'shopping.merchandise':
                    for childObject in object:
                        if childObject.attrib['name'] == 'merchandise_type':
                            merch_type = childObject.text
                        elif childObject.attrib['name'] == 'price':
                            price = childObject.text
                        elif childObject.attrib['name'] == 'image_absolute_file_path':
                            image_path = childObject.text
                    merch = Merchandise(
                        image_absolute_file_path = image_path,
                        merchandise_type = merch_type,
                        price = price
                    )
                    selected_merchandise.append(merch)
                elif object.attrib['model'] == 'shopping.feature':
                    for childObject in object:
                        if childObject.attrib['name'] == 'feature_type':
                            detectedFeature = childObject.text
                    feature = Feature(
                        merchandise_key = merch,
                        feature_type = detectedFeature
                    )
                    selected_merchandise.append(feature)
                elif object.attrib['model'] == 'shopping.orderitem':
                    for childObject in object:
                        if childObject.attrib['name'] == 'quantity':
                            detectedQuantity = childObject.text
                    orderItem = OrderItem(
                        order_key = order,
                        quantity = detectedQuantity,
                        merchandise_key = merch

                    )
                    selected_merchandise.append(orderItem)
    print("[shopping/views.py convert_session_to_list()] returning the list")
    return selected_merchandise

def convert_merchandse_list_to_session(listOfFeatures, request):
    print("[shopping/views.py convert_merchandse_list_to_session()]")
    for feature in listOfFeatures:
        print(f"{feature}")
    data = serializers.serialize("xml", listOfFeatures)
    request.session['data']=data
    print("[shopping/views.py convert_merchandse_list_to_session()] data serialized and saved to request.session[data]")

def clearCart(request):
    print(f"[shopping/views.py clearCart()]")
    keys_to_clear = [key for key in request.session.keys() if '_auth_user_' not in key]
    for key in keys_to_clear:
        print(f"[shopping/views.py clearCart()] clearing entry under request.session[{key}]")
        del request.session[key]
    keys_to_clear = [key for key in request.COOKIES.keys()]
    response = HttpResponseRedirect('/shopping')
    for key in keys_to_clear:
        print(f"[shopping/views.py clearCart()] clearing entry under request.COOKIES[{key}]")
        response.delete_cookie(key)
    return response

def print_catalogue(request):
    print(f"[shopping/views.py print_catalogue()]")
    if 'clear' in request.POST:
        print(f"[shopping/views.py print_catalogue()] clear detected in request.POST")
        return clearCart(request)

    # the shopping cart requires  sessionid to exist. to that effect, created a cookie will create a sessionid
    if 'sessionid' not in request.COOKIES:
        request.session['csss_cookie']="set"

    object_list = Merchandise.objects.all()

    context = {
        'tab': 'shopping',
        'object_list': object_list,
    }
    return render(request, 'shopping/catalogue.html', context)

def add_item_to_cart(request):
    print(f"[shopping/views.py add_item_to_cart()]")
    print(f"request.POST={request.POST}")
    if not('selected_merchandise' in request.POST and 'Color' in request.POST and 'Size' in request.POST and 'Quantity' in request.POST):
        print("[shopping/views.py add_item_to_cart()] not all keys necessary for adding item to cart are specified")
        return HttpResponseRedirect('/shopping')

    if 'selected_merchandise' in request.POST and 'Color' in request.POST and 'Size' in request.POST and 'Quantity' in request.POST:
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
            merchandise_type = request.POST['selected_merchandise']
        )

        merchandise_selected.append(merch)

        for key in request.POST.keys():
            if key != 'selected_merchandise' and key != 'csrfmiddlewaretoken' and key != 'Quantity':
                print(f"[shopping/views.py add_item_to_cart()] processing key {key} and value {request.POST[key]} for selected_merchandise selected")
                feat = Feature.objects.get(
                    merchandise_key = merch,
                    feature_type = key
                )
                merchandise_selected.append(feat)
                spec = Specification.objects.get(
                    feature_key = feat,
                    specification_type = request.POST[key]
                )
                merchandise_selected.append(spec)

        itemQuantity = OrderItem(
            order_key = merchandise_on_cart[0],
            merchandise_key = merch,
            quantity = int(request.POST['Quantity'])
        )

        merchandise_selected.append(itemQuantity)

        merchandiseFound = False
        index = 0
        while index < len(merchandise_on_cart):
            if index > 0 and not merchandiseFound:
                if hasattr(merchandise_on_cart[index], 'selected_merchandise'):
                    if merchandise_selected[0].selected_merchandise == merchandise_on_cart[index].selected_merchandise \
                            and merchandise_selected[1].feature == merchandise_on_cart[index+1].feature \
                            and merchandise_selected[2].Specification == merchandise_on_cart[index+2].Specification \
                            and merchandise_selected[3].feature == merchandise_on_cart[index+3].feature \
                            and merchandise_selected[4].Specification == merchandise_on_cart[index+4].Specification:
                                merchandiseFound = True
                                old_quantity = merchandise_on_cart[index+5].quantity
                                new_quantity = merchandise_on_cart[index+5].quantity + int(request.POST['Quantity'])
                                print(f"[shopping/views.py add_item_to_cart()] updating quantity from {old_quantity} to {new_quantity} for { merchandise_selected[0].selected_merchandise}")
                                merchandise_on_cart[index+5].quantity = new_quantity
                                index = index + 5
                    else:
                        index = index + 1
                else:
                    index = index + 1
            else:
                index = index + 1

        if not merchandiseFound:
            print(f"[shopping/views.py add_item_to_cart()] {merchandise_selected[0].merchandise_type} not found in the cart")
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
                price = float(merchandise_selected[indx].price)
            if hasattr(merchandise_selected[indx], 'quantity'):
                quantity = int(merchandise_selected[indx].quantity)
                item_total = item_total + (price * quantity)
    print(f"[shopping/views.py get_order_total_from_cache()] price calculated = {item_total}")
    return int(item_total)

def checkout_page(request):
    print(f"[shopping/views.py checkout_page()]")

    listOfFeatures=convert_session_to_list(request)

    merchandise_selected = []
    index = 0
    print(f"listOfFeatures={listOfFeatures}")
    while index < len(listOfFeatures):
            if index > 0:
                current_item = []
                current_item.append(listOfFeatures[index].image_absolute_file_path)
                current_item.append(listOfFeatures[index].merchandise_type)
                current_item.append(listOfFeatures[index].price)
                current_item.append(listOfFeatures[index+2].specification_type)
                current_item.append(listOfFeatures[index+4].specification_type)
                current_item.append(listOfFeatures[index+5].quantity)
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
            'total': get_order_total_from_cache(listOfFeatures)
        }
        print(f"[shopping/views.py checkout_page()] items detected and will be displayed")

    return render(request, 'shopping/checkout.html', context)


def update_merchandise_on_cart(selected_merchandise, size, color, quantity, merchandise_on_cart):
    print(f"[shopping/views.py update_merchandise_on_cart()] searching for {selected_merchandise} {size} {color}")
    index = 0
    while index < len(merchandise_on_cart):
        if (type(merchandise_on_cart[index]) == Merchandise) and (merchandise_on_cart[index].merchandise_type == selected_merchandise):
            print("its a merchandise!")
            index+=1
            while (index < len(merchandise_on_cart)) and (merchandise_on_cart[index] != Merchandise):
                if (type(merchandise_on_cart[index]) == Feature) and (type(merchandise_on_cart[index+1]) == Specification) and (merchandise_on_cart[index].feature_type == 'Size'):
                    if (merchandise_on_cart[index+1].specification_type) != size:
                        print(f"specification_type of {merchandise_on_cart[index+1].specification_type} did not match {size}")
                        return
                    else:
                        print("Size matched!")
                if (type(merchandise_on_cart[index]) == Feature) and (type(merchandise_on_cart[index+1]) == Specification) and (merchandise_on_cart[index].feature_type == 'Color'):
                    if (merchandise_on_cart[index+1].specification_type) != color:
                        print(f"specification_type of {merchandise_on_cart[index+1].specification_type} did not match {color}")
                        return
                    else:
                        print("color matched!")
                if (type(merchandise_on_cart[index]) == OrderItem):
                    print(f"[shopping.views update_merchandise_on_cart()] quantity updated to {quantity} for {selected_merchandise} {size} {color}")
                    merchandise_on_cart[index].quantity = quantity
                index+=1
        index+=1


def update_cart(request):
    print("[shopping/views.py update_cart()]")
    print(f"request.POST={request.POST}")
    merchandise_on_cart=convert_session_to_list(request)
    for indx, value in enumerate(request.POST.getlist('selected_merchandise')):
        selected_merchandise = value
        size = request.POST.getlist('size')[indx]
        color = request.POST.getlist('color')[indx]
        quantity = request.POST.getlist('Quantity')[indx]
        print(f"[shopping/views.py update_cart()] updating {size}, {color} and {quantity} for selected_merchandise {selected_merchandise}")
        update_merchandise_on_cart(selected_merchandise, size, color, quantity, merchandise_on_cart)
    convert_merchandse_list_to_session(merchandise_on_cart, request)
    return HttpResponseRedirect('/shopping/checkout_form')

def get_order_total(order_id):
    print("[shopping/views.py get_order_total()]")
    order = Order.objects.get(order_id=order_id)
    item_total = 0
    for item_ordered in OrderItem.objects.all().filter(order_key=order):
        item_total = item_total + ( 100 * ( item_ordered.quantity * item_ordered.merchandise_key.price ) )
    print(f"[shopping/views.py get_order_total()] price calculated = {item_total}")
    return int(item_total)

def purchase(request):
    print(f"[shopping/views.py purchase()] request.session['data']={request.session['data']}")
    existing_order=convert_session_to_list(request)
    order = None
    merch = None
    quantity = None
    merchandise_for_order = None
    feat = None

    customer = Customer(
        name = request.POST['full_name'],
        sfu_email = request.POST['sfu_email']
    )
    customer.save()
    for indx, item in enumerate(existing_order):
        print(f"encountered item {item}")
        if indx == 0:
            order = item
            order.customer_key = customer
            order.save()
            print("[shopping/views.py purchase()] order saved")
        elif (type(item) == Merchandise):
            print("its merchandise!")
            merch = Merchandise.objects.get(merchandise_type=item.merchandise_type)
            merchandise_for_order = OrderItem(
                order_key = order,
                merchandise_key = merch
            )
            merchandise_for_order.save()
            print("[shopping/views.py purchase()] OrderItem saved")
        elif (type(item) == Feature):
            print("its Feature!")
            feat = Feature.objects.get(
                feature_type = item.feature_type,
                merchandise_key_id = merch
            )
        elif (type(item) == Specification):
            print("its specification!")
            spec = Specification.objects.get(
                specification_type = item.specification_type,
                feature_key = feat
            )
            featSelect = OrderItemSpecification(
                orderItem_key = merchandise_for_order,
                feature_key = feat,
                specification_key = spec
            )
            featSelect.save()
            print("[shopping/views.py purchase()] featSelect saved")
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
                clearCart(request)
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


def remove_item(request):
    print("[shopping/views.py remove_item_from_cart()] ")

    url = request.build_absolute_uri().replace("%20", " ")

    indexOfLastSlash = url.rfind('/') + 1
    indexOfSecondLastSlash = url.rfind('/', 0, indexOfLastSlash-1) + 1
    indexOfThirdLastSlash = url.rfind('/', 0, indexOfSecondLastSlash-1) + 1
    selected_merchandise = url[indexOfThirdLastSlash:indexOfSecondLastSlash-1]
    color = url[indexOfSecondLastSlash:indexOfLastSlash-1]
    size = url[indexOfLastSlash:]

    merchandise_on_cart=convert_session_to_list(request)
    new_merchandise_list = []

    index = 0
    print(f"[shopping/views.py remove_item_from_cart()] searching for {selected_merchandise} {size} {color}")

    while index < len(merchandise_on_cart):
        if (type(merchandise_on_cart[index]) == Merchandise) and (merchandise_on_cart[index].merchandise_type == selected_merchandise):
            innerIndex=1
            matched = 0
            while (innerIndex+index < len(merchandise_on_cart) and (merchandise_on_cart[innerIndex+index] != Merchandise)):
                if (type(merchandise_on_cart[innerIndex+index]) == Feature) and (type(merchandise_on_cart[innerIndex+index+1]) == Specification) and (merchandise_on_cart[innerIndex+index].feature_type == 'Size'):
                    if (merchandise_on_cart[innerIndex+index+1].specification_type) != size:
                        print(f"specification_type of {merchandise_on_cart[innerIndex+index+1].specification_type} did not match {size}")
                    else:
                        print("Size matched!")
                        innerIndex+=2
                        matched+=1
                if (type(merchandise_on_cart[innerIndex+index]) == Feature) and (type(merchandise_on_cart[innerIndex+index+1]) == Specification) and (merchandise_on_cart[innerIndex+index].feature_type == 'Color'):
                    if (merchandise_on_cart[innerIndex+index+1].specification_type) != color:
                        print(f"specification_type of {merchandise_on_cart[innerIndex+index+1].specification_type} did not match {color}")
                    else:
                        print("color matched!")
                        matched+=1
                        innerIndex+=2
                if (matched == 2):
                    index = index + 6
                    print(f"[shopping/views.py remove_item_from_cart()] skipping over an item")
                    break
                if (matched == 0):
                    print(f"[shopping/views.py remove_item_from_cart()] 1-adding {merchandise_on_cart[index]} to the list")
                    new_merchandise_list.append(merchandise_on_cart[index])
                    index+=1
                    break
        # else:
        #     print(f"[shopping/views.py remove_item_from_cart()] 2-adding {merchandise_on_cart[index]} to the list")
        #     new_merchandise_list.append(merchandise_on_cart[index])
        #     index+=1
        # if hasattr(merchandise_on_cart[index], 'selected_merchandise'):
        #     if merchandise_on_cart[index].selected_merchandise == selected_merchandise \
        #         and merchandise_on_cart[index+1].feature == 'Size' \
        #         and merchandise_on_cart[index+2].Specification == size \
        #         and merchandise_on_cart[index+3].feature == 'Color' \
        #         and merchandise_on_cart[index+4].Specification == color:
        #         index = index + 6
        #         print(f"[shopping/views.py remove_item_from_cart()] skipping over an item")
        #     else:
        #         print(f"[shopping/views.py remove_item_from_cart()] 1-adding {merchandise_on_cart[index]} to the list")
        #         new_merchandise_list.append(merchandise_on_cart[index])
        #         index = index + 1
        else:
            print(f"[shopping/views.py remove_item_from_cart()] 2-adding {merchandise_on_cart[index]} to the list")
            new_merchandise_list.append(merchandise_on_cart[index])
            index = index + 1
    convert_merchandse_list_to_session(new_merchandise_list, request)
    return HttpResponseRedirect('/shopping/checkout_form')

def checkout_form(request):
    print(f"[shopping/views.py checkout_form()]")
    print("request.POST="+str(request.POST))
    # print("request.COOKIES="+str(request.COOKIES))
    # print("request.COOKIES.keys()="+str(request.COOKIES.keys()))
    # print("request.session="+str(request.session.keys()))
    # print("request.session.keys()="+str(request.session.keys()))
    # print("request.session.load()="+str(request.session.load()))
    if 'action' in request.POST and request.POST['action'] == 'update_cart':
        return update_cart(request)
    elif 'stripeToken' in request.POST:
        return purchase(request)
    elif 'action' in request.POST and 'remove' in request.POST['action']:
        return remove_item_from_cart(request)
    if 'clear' in request.POST:
        clearCart(request)
    return checkout_page(request)
