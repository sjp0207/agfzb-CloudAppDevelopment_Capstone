from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
# from .restapis import related methods
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
from djangoapp.restapis import *
from djangoapp.models import CarModel, CarMake, CarDealer, DealerReview

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/sjp7work%40gmail.com_dev/dealership-package/get-dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # print(dealerships)
        # Concat all dealer's short name
        # dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        # return HttpResponse(dealer_names)
        context["dealership_list"] = dealerships
    return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/sjp7work%40gmail.com_dev/dealership-package/get-reviews"
        # Get dealers from the URL
        dealer_reviews = get_dealer_reviews_from_cf(url, dealer_id)
        # # Concat all dealer's short name
        # reviews = ' '.join([review.sentiment for review in dealer_reviews])
        # Return a list of dealer short name
        # return HttpResponse(reviews)
        context["reviews"] = dealer_reviews
        context["dealer_id"] = dealer_id
    return render(request, 'djangoapp/dealer_details.html', context)


# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    context = {}
    json_payload = {}
    review = {}
    dealer_url = "https://us-south.functions.appdomain.cloud/api/v1/web/sjp7work%40gmail.com_dev/dealership-package/get-dealership"
    dealer = get_dealer_by_id_from_cf(dealer_url, id = dealer_id)
    context["dealer"] = dealer
    context["dealer_id"] = dealer_id
    if request.method == 'GET':
        cars = CarModel.objects.all()
        print(cars)
        context["cars"] = cars
        return render(request, 'djangoapp/add_review.html', context)
    elif request.method == 'POST':
        if request.user.is_authenticated:
            print(request.POST)
            username = request.user.username
            print(request.POST)
            car_name = request.POST["car"]
            car = CarModel.objects.get(name=car_name)
            review["time"] = datetime.utcnow().isoformat()
            review["name"] = username
            review["dealership"] = dealer_id
            review["id"] = car.id + '__' + datetime.utcnow().isoformat()
            review["review"] = request.POST["content"]
            review["purchase"] = False
            if "purchasecheck" in request.POST:
                review["purchase"] = True
                print(request.POST.get("purchasedate"))
                review["purchase_date"] = datetime.strptime(request.POST.get("purchasedate"), "%m/%d/%Y").isoformat()
                review["car_make"] = car.make.name
                review["car_model"] = car.name
                review["car_year"] = int(car.year.strftime("%Y"))

            json_payload["review"] = review
            json.dumps(json_payload)
            post_request("https://us-south.functions.appdomain.cloud/api/v1/web/sjp7work%40gmail.com_dev/dealership-package/post-review",json_payload)
        return redirect("djangoapp:dealer_details", dealer_id=dealer_id) 
