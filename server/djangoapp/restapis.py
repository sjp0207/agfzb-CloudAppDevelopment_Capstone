import requests
import json
# import related models here
from requests.auth import HTTPBasicAuth
from .models import CarModel, CarMake, CarDealer, DealerReview
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions, SentimentOptions
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    # print(kwargs)
    # print("GET from {} ".format(url))
    
    try:
        response = requests.get(url, params=kwargs, headers={'Content-Type': 'application/json'})
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload):
    try:
        response = requests.post(url, json=json_payload)
    except:
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    print(json_data)
    return json_data



# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    state = kwargs.get("state")
    if state:
        json_result = get_request(url, state=state)
    else:
        json_result = get_request(url)
    if json_result:
        dealers = json_result
        
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
def get_dealer_by_id_from_cf(url, **kwargs):
    result = {}
    id = kwargs.get("id")
    if id:
        json_result = get_request(url, id=id)
    else:
        json_result = get_request(url)
    if json_result:
        dealer_doc = json_result[0]
        dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
    result = dealer_obj
    return result

# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, dealer_id):
    results = []
    if id:
        json_result = get_request(url, dealerId=dealer_id)

    if json_result:
        reviews = json_result["data"]["docs"]
        
        for review in reviews:
            # Get its content in `doc` object
            review_doc = review

            # Create a  object with values in `doc` object
            review_obj = DealerReview(dealership=review_doc["dealership"], name=review_doc["name"], purchase=review_doc["purchase"],
                                   review=review_doc["review"], purchase_date=review_doc["purchase_date"], car_make=review_doc["car_make"],
                                   car_model=review_doc["car_model"],car_year=review_doc["car_year"], sentiment='',id=review_doc["id"])
            review_obj.sentiment = analyze_review_sentiments(review_obj.review)
            results.append(review_obj)

    return results


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(text): 
    url = "https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/7cf82d0c-ab2a-4905-82e5-18e2d0a26f21" 
    api_key = "rN7KOhcEMNBF2kLOFrqHZZgCBaxzPZYgnwcOLU-Dn4Sc" 
    authenticator = IAMAuthenticator(api_key) 
    natural_language_understanding = NaturalLanguageUnderstandingV1(version='2022-04-07',authenticator=authenticator) 
    natural_language_understanding.set_service_url(url) 
    nlu_response = natural_language_understanding.analyze(
            text=text,
            features=Features(sentiment=SentimentOptions(targets=[text])),
            language='en'
        ).get_result()
    label=json.dumps(nlu_response, indent=2) 
    label = nlu_response['sentiment']['document']['label'] 

    return(label) 


