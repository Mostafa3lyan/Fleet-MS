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
import gridfs
from PIL import Image
import io


client = pymongo.MongoClient('mongodb+srv://mostafa:Mo12312300@fleetmanagementsystem.5xv0klr.mongodb.net/test')
dbname = client['FleetManagementSystem']

# Collections
customers = dbname["Customer"]
drivers = dbname["Driver"]
products = dbname["Item"]
menus = dbname["Menu"]
businesses = dbname["Business"]
orders = dbname["Order"]
business_reviews = dbname["business_reviews"]
fs = gridfs.GridFS(dbname)



# @csrf_exempt
# def add_item(request):
#     if request.method == 'POST':
#         data = json.loads(request.body) 
#         menu_id = data.get('menu_id')
#         title = data.get('title')
#         price = data.get('price')
#         category = data.get('category')
#         image = data.get('image')
#         description = data.get('description')
#         available = data.get('available')
#         item = {
#             "title": title,
#             "price": price,
#             "category": category,
#             "image": image,
#             "description": description,
#             "available": available,
#         }
#         item_id = products.insert_one(item).inserted_id
#         menus.find_one_and_update({"_id": ObjectId(menu_id)}, {'$push': {'items': item_id}})
#         return JsonResponse({'message': 'Item added successfully'})
#     else:
#         return JsonResponse({'error': 'Invalid request method'})
    
    
@csrf_exempt
def add_item(request):
    if request.method == 'POST':
        data = json.loads(request.body) 
        menu_id = data.get('menu_id')
        title = data.get('title')
        price = data.get('price')
        category = data.get('category')
        description = data.get('description')
        available = data.get('available')
        
        # Get the uploaded image from the request
        image = request.FILES.get('image')
        
        if image:
            # Open the image using PIL and convert it to JPEG format
            img = Image.open(io.BytesIO(image.read()))
            img = img.convert('RGB')
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=95)
            image_binary = output.getvalue()
            
            # Store the image in MongoDB using GridFS
            image_id = fs.put(image_binary, filename=image.name)
            item = {
                "title": title,
                "price": price,
                "category": category,
                "image_id": str(image_id),
                "description": description,
                "available": available,
            }
        else:
            item = {
                "title": title,
                "price": price,
                "category": category,
                "description": description,
                "available": available,
            }
        
        item_id = products.insert_one(item).inserted_id
        menus.find_one_and_update({"_id": ObjectId(menu_id)}, {'$push': {'items': item_id}})
        return JsonResponse({'message': 'Item added successfully'})
    else:
        return JsonResponse({'error': 'Invalid request method'})
    
    
    


@csrf_exempt
def get_item(request, item_id):
    if request.method == 'GET':
        item = products.find_one({"_id": ObjectId(item_id)})
        if item:
            return JsonResponse(json.loads(json_util.dumps(item)), safe=False)
        else:
            return JsonResponse({'error': 'Item not found'})
    else:
        return JsonResponse({'error': 'Method not allowed'})

@csrf_exempt
def edit_item(request, item_id):
    if request.method == "PATCH":
        data = json.loads(request.body)
        title = data.get("title", None)
        price = data.get("price", None)
        category = data.get("category", None)
        image = data.get("image", None)
        description = data.get("description", None)
        available = data.get("available", None)

        item = products.find_one({"_id": ObjectId(item_id)})
        if not item:
            return JsonResponse({"message": "Item not found"})

        new_item = {
            "title": title or item["title"],
            "price": price or item["price"],
            "category": category or item["category"],
            "image": image or item["image"],
            "description": description or item["description"],
            "available": available or item["available"]
        }

        products.update_one({"_id": ObjectId(item_id)}, {"$set": new_item})
        return JsonResponse({"message": "Item edited successfully"})

    return JsonResponse({"message": "Invalid request method"})


@csrf_exempt
def delete_item(request, menu_id, item_id):
    if request.method == "DELETE":
        item = products.find_one({"_id": ObjectId(item_id)})
        if not item:
            return JsonResponse({"message": "Item not found"})

        menus.update_one({"_id": ObjectId(menu_id)}, {"$pull": {"items": ObjectId(item_id)}})
        products.delete_one({"_id": ObjectId(item_id)})
        return JsonResponse({"message": "Item deleted successfully"})

    return JsonResponse({"message": "Invalid request method"})


@csrf_exempt
def confirm_order(request, order_id):
    if request.method == "POST":
        data = json.loads(request.body)
        # Extract business ID from POST request
        business_id = data.get("business_id")
        if not business_id:
            return JsonResponse({"message": "Business ID missing from request"}, status=400)

        # Find order by ID and check if it's already confirmed
        order = orders.find_one({'_id': ObjectId(order_id)})
        if not order:
            return JsonResponse({"message": "Order not found"}, status=400)
        if order.get('status') == 'confirmed':
            return JsonResponse({"message": "Order already confirmed"}, status=400)

        # Update order status and business status
        orders.update_one(
            {'_id': ObjectId(order_id)},
            {'$set': {'status': 'confirmed', 'business_id': ObjectId(business_id)}})
        return JsonResponse({"message": "Order confirmed successfully"})
    
    return JsonResponse({"message": "Invalid request method"}, status=400)


# def assign_order_to_nearest_driver(business_id, order_id):
#     business = businesses.find_one({"_id": ObjectId(business_id)})
#     business_location = (business['latitude'], business['longitude'])

#     drivers_locations = []
#     for driver in drivers.find({"status": "available"}):
#         drivers_locations.append((driver['latitude'], driver['longitude']))

#     if not drivers_locations:
#         return HttpResponse("No available drivers found.")

#     closest_driver_location = min(drivers_locations, key=lambda loc: haversine(business_location, loc))

#     driver = drivers.find_one_and_update(
#         {"latitude": closest_driver_location[0], "longitude": closest_driver_location[1], "status": "available"},
#         {"$set": {"status": "unavailable"}}
#     )

#     if not driver:
#         return HttpResponse("Unable to assign order to a driver.")

#     orders.update_one({"_id": ObjectId(order_id)}, {"$set": {"driver_id": driver['_id']}})

#     return HttpResponse(f"Order assigned to driver {driver['_id']}.")

# def haversine(point1, point2):
#     # Calculate the great circle distance between two points on the earth (in km)
#     lat1, lon1 = point1
#     lat2, lon2 = point2
#     dlat = math.radians(lat2 - lat1)
#     dlon = math.radians(lon2 - lon1)
#     a = sin(dlat / 2) ** 2 + cos(math.radians(lat1)) * cos(math.radians(lat2)) * sin(dlon / 2) ** 2
#     c = 2 * math.atan2(sqrt(a), sqrt(1 - a))
#     return 6371 * c  # Earth radius is 6371 km


# def confirm_order(order_id):
#     order = orders.find_one({"_id": ObjectId(order_id)})
#     if not order:
#         return HttpResponse("Order not found.")
#     if order['status'] != 'pending':
#         return HttpResponse("Order has already been confirmed or assigned to a driver.")

#     business_id = order['business_id']
#     assign_order_to_nearest_driver(business_id, order_id)

#     orders.update_one({"_id": ObjectId(order_id)}, {"$set": {"status": "confirmed"}})

#     return HttpResponse("Order confirmed and assigned to driver.")





@csrf_exempt
def cancel_order(request, order_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        # Get the cancellation reason from the request POST data
        cancellation_reason = data.get('cancellation_reason')

        # Find the order document with the given ID
        order = orders.find_one({'_id': ObjectId(order_id)})
        if not order:
            return JsonResponse({'error': 'Invalid order ID'})

        # Check if the order can be cancelled
        if order.get('status') not in ['pending', 'confirmed']:
            return JsonResponse({'error': 'Cannot cancel order'})

        # Update the status and cancellation_reason attributes of the order document
        orders.update_one({'_id': ObjectId(order_id)}, {'$set': {'status': 'cancelled', 'cancellation_reason': cancellation_reason}})

        return JsonResponse({'message': 'Order cancelled successfully'})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)



@csrf_exempt
def get_order_details(request, order_id):
    if request.method == "GET":
        # Find order with given ID in database
        order = orders.find_one({"_id": ObjectId(order_id)})
        if not order:
            return JsonResponse({"message": "Order not found"}, status=404)

        # Extract relevant fields from order document
        order_details = {
            "order_id": str(order["_id"]),
            "customer_id": str(order["customer_id"]),
            "total_cost": order["total_cost"],
            "items": order["items"],
            "status": order["status"],
            "date": order["date"],
            "delivery_address": order["delivery_address"]
        }

        # Convert the MongoDB document to JSON format
        order_details_json = json_util.dumps(order_details)

        return JsonResponse(order_details_json, safe=False)

    return JsonResponse({"message": "Invalid request method"}, status=400)


@csrf_exempt
def view_orders_history(request, business_id):
    if request.method == 'GET':
        # Extract relevant fields from business document
        orders_cursor = dbname["Order"].find({"business_id": ObjectId(business_id)})
        orders = list(orders_cursor)
        orders_details = []
        for order in orders:
            order_details = {
                'order_id': str(order['_id']),
                'customer_id': str(order['customer_id']),
                'total_cost': order['total_cost'],
                'items': order['items'],
                'status': order['status'],
                'date': order['date'],
                'delivery_address': order['delivery_address']
            }
            
            orders_details.append(order_details)
        return JsonResponse({'orders':json_util.dumps (orders_details)})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)



@csrf_exempt
def view_business_reviews(request, business_id):
    if request.method == 'GET':
        my_business_reviews = []
        for review in business_reviews.find({"business_id": ObjectId(business_id)}):
            my_business_reviews.append(review)
        return JsonResponse({"reviews": json_util.dumps(my_business_reviews)})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)



@csrf_exempt
def add_comment_to_review(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        review_id = ObjectId(data.get('review_id'))
        comment = data.get('comment')

        review = business_reviews.find_one({"_id": review_id})
        # check if the review exists
        if review is None:
            return JsonResponse({"message": "Review not found"}, status=404)

        # add the comment to the review's "comments" list
        comments = review.get("comments", [])
        comments.append(comment)

        # update the review with the new comments list
        business_reviews.update_one({"_id": review_id}, {"$set": {"comments": comments}})
        return JsonResponse({"message": "Comment added successfully"})
    else:
        return JsonResponse({"message": "Invalid request method"}, status=400)
    
    
    

#track driver