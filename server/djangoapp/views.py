# Uncomment the required imports before adding the code

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from datetime import datetime
from .restapis import get_request, analyze_review_sentiments, post_review
from django.http import JsonResponse
from django.contrib.auth import login, authenticate
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from .models import CarMake, CarModel
from .populate import initiate



# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    # Get username and password from request.POST dictionary
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    # Try to check if provide credential can be authenticated
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        # If user is valid, call login method to login current user
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)

# Create a `logout_request` view to handle sign out request
# def logout_request(request):
# ...

# Create a `registration` view to handle sign up request
# @csrf_exempt
# def registration(request):
# ...

# # Update the `get_dealerships` view to render the index page with
# a list of dealerships
# def get_dealerships(request):
# ...

def get_dealerships(request, state="All"):
    if(state == "All"):
        endpoint = "/fetchDealers"
    else:
        endpoint ="/fetchDealers/"+state
    dealerships = get_request(endpoint)
    return JsonResponse({"status":200,"dealers":dealerships})

# Create a `get_dealer_reviews` view to render the reviews of a dealer
# def get_dealer_reviews(request,dealer_id):
# ...


        
def get_dealer_reviews(request, dealer_id):
    print(f"DEBUG: Getting reviews for dealer_id: {dealer_id}")
    print(f"DEBUG: dealer_id type: {type(dealer_id)}")
    if (dealer_id):
        endpoint = f'/fetchReviews/dealer/{dealer_id}'
        print(f"DEBUG: Calling endpoint: {endpoint}")
        reviews = get_request(endpoint)
        print(f"DEBUG: Reviews returned: {reviews}")
    if reviews is None:
        [rint(f"DEBUG: Reviews is None: returning empty array")]
        return JsonResponse({"status": 200, "reviews": []})
        print(f"DEBUG: Processing {len(reviews)} reviews")
    for review_detail in reviews:
        response = analyze_review_sentiments(review_detail['review'])
        print(f"DEBUG: Sentiment response: {response}")
        review_detail['sentiment'] = response['sentiment']
    print(f"DEBUG: Returning {len(reviews)} reviews")
    return JsonResponse({"status":200,"reviews": reviews})

    
# Create a `get_dealer_details` view to render the dealer details
# def get_dealer_details(request, dealer_id):
# ...

def get_dealer_details(request, dealer_id):
    if (dealer_id):
        endpoint = f'/fetchDealer/{dealer_id}'
        dealership = get_request(endpoint)
        return JsonResponse({"status":200,"dealer":dealership})
    else:
        return JsonResponse({"status":400,"message":"Bad Request"})

# Create a `add_review` view to submit a review
# def add_review(request):
# ...

def add_review(request):
    if (request.user.is_anonymous == False):
        data = json.loads(request.body)
        print(f'"=" * 50')
        print("ADD_REVIEW VIEW CALLED")
        print(f"User: {request.user.username}")
        print(f"Data received: {data}")
        print(f"=" *50)
        try:
            response = post_review(data)
            print(f"post_review returned: {response}")
            return JsonResponse({"status":200})
        except Exception as e:
            print(f"ERROR in add_review: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({"status":401,"message":"Error in posting review"})
    else:
        return JsonResponse({"status":403, "message": "Unauthorized"})


def get_cars(request):
    count = CarMake.objects.filter().count()
    print(count)
    if (count == 0):
        initiate()
    car_models = CarModel.objects.select_related('car_make')
    cars = []
    for car_model in car_models:
        cars.append({'CarModel': car_model.name, "CarMake": car_model.car_make.name})
    return JsonResponse({"CarModels":cars})