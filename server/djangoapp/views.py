from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import login, authenticate
from django.views.decorators.csrf import csrf_exempt
from .restapis import get_request, analyze_review_sentiments, post_review
import logging
import json
from .models import CarMake, CarModel
from .populate import initiate


# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    # Get username and password from request body
    data = json.loads(request.body)
    username = data["userName"]
    password = data["password"]

    # Try to check if provided credentials can be authenticated
    user = authenticate(username=username, password=password)
    result = {"userName": username}
    if user is not None:
        # If user is valid, log them in
        login(request, user)
        result = {"userName": username, "status": "Authenticated"}
    return JsonResponse(result)

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
    if state == "All":
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/" + state

    dealerships = get_request(endpoint)
    return JsonResponse({"status": 200, "dealers": dealerships})

# Create a `get_dealer_reviews` view to render the reviews of a dealer
# def get_dealer_reviews(request,dealer_id):
# ...


        
def get_dealer_reviews(request, dealer_id):
    logger.debug("Getting reviews for dealer_id: %s", dealer_id)

    reviews = None
    if dealer_id:
        endpoint = f"/fetchReviews/dealer/{dealer_id}"
        logger.debug("Calling endpoint: %s", endpoint)
        reviews = get_request(endpoint)
        logger.debug("Reviews returned: %s", reviews)

    if not reviews:
        logger.debug("Reviews is None or empty: returning empty list")
        return JsonResponse({"status": 200, "reviews": []})

    for review_detail in reviews:
        response = analyze_review_sentiments(review_detail.get("review", ""))
        logger.debug("Sentiment response: %s", response)
        review_detail["sentiment"] = response.get("sentiment") if response else None

    logger.debug("Returning %d reviews", len(reviews))
    return JsonResponse({"status": 200, "reviews": reviews})

    
# Create a `get_dealer_details` view to render the dealer details
# def get_dealer_details(request, dealer_id):
# ...

def get_dealer_details(request, dealer_id):
    if dealer_id:
        endpoint = f"/fetchDealer/{dealer_id}"
        dealership = get_request(endpoint)
        return JsonResponse({"status": 200, "dealer": dealership})
    return JsonResponse({"status": 400, "message": "Bad Request"})

# Create a `add_review` view to submit a review
# def add_review(request):
# ...

def add_review(request):
    if not request.user.is_anonymous:
        data = json.loads(request.body)
        logger.info("ADD_REVIEW VIEW CALLED by %s", request.user.username)
        logger.debug("Data received: %s", data)
        try:
            response = post_review(data)
            logger.debug("post_review returned: %s", response)
            return JsonResponse({"status": 200})
        except Exception as e:
            logger.exception("ERROR in add_review: %s", e)
            return JsonResponse({"status": 401, "message": "Error in posting review"})
    return JsonResponse({"status": 403, "message": "Unauthorized"})


def get_cars(request):
    count = CarMake.objects.count()
    logger.debug("CarMake count: %d", count)
    if count == 0:
        initiate()

    car_models = CarModel.objects.select_related("car_make")
    cars = []
    for car_model in car_models:
        cars.append({"CarModel": car_model.name, "CarMake": car_model.car_make.name})

    return JsonResponse({"CarModels": cars})