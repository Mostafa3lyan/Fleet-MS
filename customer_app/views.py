from cmath import *
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests
import math
from bson import json_util
from bson.objectid import ObjectId
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import datetime
# from utilities.mongodb import *
import pymongo


client = pymongo.MongoClient(
    'mongodb+srv://mostafa:Mo12312300@fleetmanagementsystem.5xv0klr.mongodb.net/test')
db = client['FleetManagementSystem']

# Collections
users = db["User"]
customers = db["Customer"]
products = db["Item"]
menus = db["Menu"]
businesses = db["Business"]
orders = db["Order"]
business_reviews = db["business_reviews"]


@csrf_exempt
def createCustomer(request):
    if request.method == 'POST':
        # Get the incoming data from the request
        data = json.loads(request.body)
        # Insert the document into the MongoDB collection
        result = customers.insert_one(data)
        # Return a JSON response with the inserted document ID
        return JsonResponse({'id': str(result.inserted_id)})
    else:
        return JsonResponse(status=405)


@csrf_exempt
def login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        user = customers.find_one({"email": email, "password": password})
        if user:
            # User exists and password matches, redirect to home page
            return JsonResponse(data, status=200)
        else:
            # User does not exist or password does not match, show error message
            return JsonResponse({'success': False, 'message': 'Invalid email or password'})


@csrf_exempt
def create_new_account(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        password = data.get('password')
        email = data.get('email')
        phone = data.get('phone')
        address = data.get('address')
        if customers.find_one({"email": email}):
            # User already exists, show error message
            # messages.error(request, 'User with this email already exists')
            return JsonResponse({'success': False, 'message': 'User with this email already exists'})
            # return JsonResponse(name, status=402)
        else:
            # Insert the new user and redirect to home page
            customer = {
                "name": name,
                "password": password,
                "email": email,
                "phone": phone,
                "address": address
            }
           # customers.insert_one(customer)
            result = customers.insert_one(data)
            return JsonResponse({'id': str(result.inserted_id)})
            # messages.success(request, 'Account created successfully')
           # return JsonResponse(name, status=200)
    else:
        return JsonResponse(name, status=400)


@csrf_exempt
def change_password(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        customer_obj = customers.find_one({"email": email})
        if not customer_obj:
            return JsonResponse({'error': 'User with this email does not exist'})
        if customer_obj.get('password') != old_password:
            return JsonResponse({'error': 'Old password does not match'})
        customers.update_one({"_id": customer_obj['_id']}, {
                             "$set": {"password": new_password}})
        return JsonResponse({'message': 'Password updated successfully'})
    else:
        return render(request, 'update_password.html')

# function to edit customer account
# expected to get document with the new data the user want to change from the frontend
# and get the id for the user we want to update
# example new_data = { 'name' : new name, 'password' : new password, etc.... }


@csrf_exempt
def edit_account(request, user_id):
    if request.method == 'PATCH':
        data = json.loads(request.body)
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        address = data.get('address')
        new_data = {
            "name": name,
            "email": email,
            "phone": phone,
            "address": address
        }
        customer_obj = customers.find_one({"_id": ObjectId(user_id)})
        if not customer_obj:
            return JsonResponse({'error': 'User with this id does not exist'})
        customers.update_one({"_id": customer_obj['_id']}, {'$set': new_data})
        return JsonResponse({'message': 'Account updated successfully'})
    else:
        customer_obj = customers.find_one({"_id": ObjectId(user_id)})
        if not customer_obj:
            return JsonResponse({'error': 'User with this id does not exist'})
        context = {'customer': customer_obj}
        return render(request, 'edit_account.html', context)


@csrf_exempt
def delete_account(request, user_id):
    customer = customers.find_one({"_id": ObjectId(user_id)})
    if not customer:
        return JsonResponse({'error': 'User with this id does not exist'})
    else:
        customers.delete_one({"_id": customer["_id"]})
        return JsonResponse({'message': 'Account deleted successfully'})


def get_product_details(request, menu_id):
    # find the menu with the given ID
    menu = menus.find_one({"_id": ObjectId(menu_id)})

    # get the product IDs for the menu
    product_ids = menu["items"]

    # get the products for the menu by querying the "products" collection
    products_details = []
    for product_id in product_ids:
        product = products.find_one({"_id": ObjectId(product_id)})
        products_details.append(product)

    # convert the list of MongoDB documents to a list of dictionaries
    products_dict = json.loads(json_util.dumps(products_details))

    # return the list of dictionaries as a JSON response
    return JsonResponse(products_dict, safe=False)


def search_for_restaurant(request, restaurant_name):

    restaurant = businesses.find_one(
        {"name": restaurant_name, "type": "restaurant"})
    restaurant = json.loads(json_util.dumps(restaurant))
    if not restaurant:
        return JsonResponse({'message': 'No restaurant found with the given name.'})
    else:
     return JsonResponse(restaurant, safe=False)


def search_for_market(request, market_name):
    market = businesses.find_one({"name": market_name, "type": "market"})
    market = json.loads(json_util.dumps(market))
    if not market:
        return JsonResponse({'message': 'No market found with the given name.'})

    return JsonResponse(market, safe=False)


@csrf_exempt
def browse_menus(request):
    if request.method == 'GET':
        menu_list = []
        for menu in menus.find():
            menu_list.append(json_util.loads(json_util.dumps(menu)))
        return JsonResponse({"menu_list": json_util.dumps(menu_list)})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def add_item_to_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        customer_id = data.get('customer_id')
        product_id = data.get('product_id')
        product_quantity = int(data.get('product_quantity'))
        business_id = data.get('business_id')
        # Find the customer document with the given customer id
        customer = customers.find_one({'_id': ObjectId(customer_id)})
        if not customer:
            return JsonResponse({'success': False})

        # Find the product document with the given ID
        product = products.find_one({'_id': ObjectId(product_id)})
        if not product:
            return JsonResponse({'success': False})

        # Add the product and quantity to the customer's cart
        cart = customer.get('cart', [])
        cart_item = {
            'product_id': product['_id'], 'quantity': product_quantity , 'business_id': business_id }
        if cart_item not in cart:
            cart.append(cart_item)
        customers.update_one({'_id': customer['_id']}, {
                             '$set': {'cart': cart}})

        return JsonResponse({'success': True})


def edit_cart(request):
    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        cart_items = request.POST.get('cart_items')

        # Convert the cart items JSON string to a list of dictionaries
        cart_items = json.loads(cart_items)

        customer = customers.find_one({'_id': ObjectId(customer_id)})
        if not customer:
            return JsonResponse({'success': False})

        # Update the cart items
        cart = customer.get('cart', [])
        for item in cart_items:
            product_id = item['product_id']
            quantity = item['quantity']
            # If quantity is 0, remove the cart item
            if quantity == 0:
                cart = [x for x in cart if x['product_id']
                        != ObjectId(product_id)]
            else:
                # Otherwise, update the quantity of the cart item
                cart_item = next(
                    (x for x in cart if x['product_id'] == ObjectId(product_id)), None)
                if cart_item:
                    cart_item['quantity'] = quantity
                else:
                    cart_item = {'product_id': ObjectId(
                        product_id), 'quantity': quantity}
                    cart.append(cart_item)

            # Update the cart item in the database
            customer.update_one({'_id': customer['_id'], 'cart.product_id': ObjectId(product_id)},
                                {'$set': {'cart.$.quantity': quantity},
                                    '$setOnInsert': {'cart.$': cart_item}},
                                upsert=True)

        # Update the user's cart in the database
        customer.update_one({'_id': customer['_id']}, {'$set': {'cart': cart}})

        return JsonResponse({'success': True})


def view_cart(request):
    if request.method == 'GET':
        data = json.loads(request.body)
        customer_id = data.get('customer_id')
        # Find the user document with the given username
        customer = customers.find_one({'_id': ObjectId(customer_id)})
        if not customer:
            return JsonResponse({'success': False})

        # Get the cart items
        cart = customer.get('cart', [])

        # Get the product details for each cart item
        products_details = []
        for item in cart:
            product_id = item['product_id']
            quantity = item['quantity']
            product = products.find_one({'_id': product_id})
            if product:
                products_details.append({'product_id': str(product_id), 'title': product['title'], 'price': product['price'],
                                         'image': product['image'], 'description': product['description'],
                                         'category': product['category'], 'quantity': quantity})
        return JsonResponse(products_details, safe=False)


@csrf_exempt
def clear_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        customer_id = data.get('customer_id')
        customer = customers.find_one({'_id': ObjectId(customer_id)})
        if not customer:
            return JsonResponse({'success': False, 'message': 'Customer not found'})

        # clear the cart for this customer
        customers.update_one({'_id': customer['_id']}, {'$set': {'cart': []}})

        return JsonResponse({'success': True, 'message': 'Cart cleared successfully'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})

# order status
# pending: The order has been received but has not yet been confirmed.
# Confirmed: The order has been confirmed and is being processed.
# In transit: The order has been shipped or is being delivered.
# Delivered: The order has been delivered to the customer.
# Cancelled: The order has been cancelled by either the customer or the business.
# Refunded: The order has been refunded due to an issue with the product or service.
# On hold: The order is temporarily on hold, usually due to an issue with payment or a product being out of stock.


@csrf_exempt
def checkout(request):
    if request.method == 'POST':
        # Get the customer ID and delivery address from the request POST data
        data = json.loads(request.body)
        customer_id = data.get('customer_id')
        delivery_address = data.get('delivery_address')

        # Find the user document with the given customer ID
        customer = customers.find_one({'_id': ObjectId(customer_id)})
        if not customer:
            return HttpResponse('Invalid customer ID')

        # Get the cart items
        cart = customer.get('cart', [])

        # Calculate the total cost of the order
        total_cost = 0
        business_id = None
        for item in cart:
            product_id = item['product_id']
            quantity = item['quantity']
            business_id = item["business_id"]
            product = products.find_one({'_id': ObjectId(product_id)})
            if product:
                total_cost += quantity * float(product['price'])

        # Get the pickup address from the business
        business = businesses.find_one({"_id": ObjectId(business_id)})
        if not business:
            return HttpResponse('Invalid business ID')
        pick_address = business.get("address")

        # Get the current date and time
        now = datetime.now()

        # Create an order document
        order = {
            'customer_id': customer_id,
            'items': cart,
            'total_cost': total_cost,
            'status': 'pending',
            'pickup_address': pick_address,
            'date': now.strftime('%Y-%m-%d %H:%M:%S'),
            'delivery_address': delivery_address
        }

        # Insert the order document into the orders collection
        result = orders.insert_one(order)
        if not result.inserted_id:
            return HttpResponse('Failed to place order')

        # Clear the user's cart
        customers.update_one({'_id': ObjectId(customer_id)}, {'$set': {'cart': []}})

        return HttpResponse('Order placed successfully')
    else:
        return render(request, 'place_order.html')


def calculate_cost(delivery_address, pick_address):
    # use Google Maps API to get the latitude and longitude of the addresses
    url = f'https://maps.googleapis.com/maps/api/geocode/json?address={delivery_address}&key=AIzaSyAv4TshMqyQUcBc_oWM6w9hjlxIKqiUOvA'
    response = requests.get(url)
    delivery_location = response.json()['results'][0]['geometry']['location']
    lat1, lon1 = delivery_location['lat'], delivery_location['lng']

    url = f'https://maps.googleapis.com/maps/api/geocode/json?address={pick_address}&key=AIzaSyAv4TshMqyQUcBc_oWM6w9hjlxIKqiUOvA'
    response = requests.get(url)
    pick_location = response.json()['results'][0]['geometry']['location']
    lat2, lon2 = pick_location['lat'], pick_location['lng']

    # calculate the distance between the two points using the haversine formula
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = 6371 * c

    cost = distance * 5
    return cost


# pick_order function : used if customer want to get order from external business that's not in our database
# it need to get delivery_address and pick_address and description of what the customer want
# and the cost can be calculeted by the function calculate_cost assuming that the cost of 1 km is 5 pounds

@csrf_exempt
def pick_order(request):
    if request.method == 'POST':
        try:
            # Get the request data
            data = json.loads(request.body)
            customer_id = data['customer_id']
            description = data['description']
            delivery_address = data['delivery_address']
            pick_address = data['pick_address']
            
            # Find the user document with the given customer_id
            customer = customers.find_one({'_id': ObjectId(customer_id)})
            if not customer:
                return JsonResponse({'error': 'Customer not found'}, status=404)

            # Get the current date and time
            now = datetime.now()
            cost = calculate_cost(delivery_address, pick_address)
            # Create an order document
            order = {
                'customer_id': customer_id,
                'description': description,
                'status': 'In transit',
                'date': now.strftime('%Y-%m-%d %H:%M:%S'),
                'delivery_address': delivery_address,
                'pick_address': pick_address,
                'pick_order_cost': cost,
            }

            # Insert the order document into the orders collection
            result = orders.insert_one(order)
            if not result.inserted_id:
                return JsonResponse({'error': 'Failed to create order'}, status=500)

            return JsonResponse({'message': 'Order placed successfully', 'order_id': str(result.inserted_id)}, status=201)


        except KeyError:
            return JsonResponse({'error': 'Invalid request data'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def cancel_order(request, order_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        # Get the cancellation reason from the request POST data
        cancellation_reason = data.get('cancellation_reason')

        # Find the order document with the given ID
        order = orders.find_one({'_id': ObjectId(order_id)})
        if not order:
            return HttpResponse('Invalid order ID')

        # Check if the order can be cancelled
        if order.get('status') not in ['pending']:
            return HttpResponse('Cannot cancel order')

        # Update the status and cancellation_reason attributes of the order document
        orders.update_one({'_id': ObjectId(order_id)}, { '$set': {'status': 'cancelled', 'cancellation_reason': cancellation_reason}})

        return HttpResponse('Order cancelled successfully')
    else:
        return render(request, 'cancel_order.html', {'order_id': order_id})


def track_order(request, order_id):
    # Find the order document with the given ID
    order = orders.find_one({'_id': ObjectId(order_id)})
    if not order:
        return HttpResponse('Invalid order ID')

    # Check if the order is in transit
    if order.get('status') != 'in transit':
        return HttpResponse('Order is not in transit')

    # Get the delivery address from the order document
    delivery_address = order.get('delivery_address')

    # you need to covert the delivery location and the driver current location to latitude and longitude
    # then you need to view both on the map (all of this by google maps api)
    # This code returns a simple response with the map location
    return HttpResponse('Map location')


@csrf_exempt
def add_order_review(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        order_id = ObjectId(data['order_id'])
        feedback = data['feedback']
        rating = int(data['rating'])
        delivery_person_rating = int(data['delivery_person_rating'])
        delivery_person_feedback = data['delivery_person_feedback']

        order = orders.find_one({'_id': order_id})
        if not order:
            return JsonResponse({'success': False, 'message': 'Order not found'})

        # Check if the order has been delivered
        if order.get('status') != 'delivered':
            return JsonResponse({'success': False, 'message': 'Order has not been delivered yet'})
        

        # Update the delivery_review attribute of the order document
        orders.update_one(
            {'_id': order_id},
            {'$set': {
                'rating': rating,
                'feedback': feedback,
                'delivery_person_rating': delivery_person_rating,
                'delivery_person_feedback': delivery_person_feedback
            }}
        )
        return JsonResponse({'success': True, 'message': 'Review added successfully'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})


@csrf_exempt
def add_business_review(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        customer_id = ObjectId(data['customer_id'])
        business_id = ObjectId(data['business_id'])
        review_text = data['review_text']
        rating = int(data['rating'])

        business = businesses.find_one({'_id': business_id})
        if not business:
            return JsonResponse({'success': False, 'message': 'Business not found'})

        business_review = {
            'business_id': business_id,
            'review_text': review_text,
            'rating': rating,
            'customer_id': customer_id,
            'created_at': datetime.now()
        }
        business_reviews.insert_one(business_review)
        return JsonResponse({'success': True, 'message': 'Review added successfully'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})

# @csrf_exempt
# def browse_menus(request):
#     if request.method == 'GET':
#         data = json.loads(request.body)
#         # Get the menu_id parameter from the query string
#         menu_id = data.get('menu_id')

#         # Retrieve the menus based on the menu_id parameter
#         if menu_id:
#             menu = menus.find_one({'_id': ObjectId(menu_id)})
#             if menu:
#                 return JsonResponse(json.loads(json_util.dumps(menu)))
#             else:
#                 return HttpResponse(status=404)
#         else:
#             menu_list = []
#             for menu in menus.find():
#                 menu_list.append(json.loads(json_util.dumps(menu)))
#             return JsonResponse({'menu_list': menu_list}, safe=False)

#browse menus


