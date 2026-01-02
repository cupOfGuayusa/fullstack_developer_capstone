# Uncomment the imports below before you add the function code
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

backend_url = os.getenv(
    'backend_url', default="http://localhost:3030")
sentiment_analyzer_url = os.getenv(
    'sentiment_analyzer_url',
    default="http://localhost:5050/")

# def get_request(endpoint, **kwargs):
# Add code for get requests to back end

def get_request(endpoint, *kwargs):
    params = ""
    if(kwargs):
        for key,value in kwargs.items():
            params=params.key+"="+value+"&"
        
    request_url =  backend_url+endpoint+"?"+params

    print("GET from {} ".format(request_url))
    try:
        response = requests.get(request_url)
        return response.json()
    except:
        print("Network exeception occured")
        return None

# def analyze_review_sentiments(text):
# request_url = sentiment_analyzer_url+"analyze/"+text
# Add code for retrieving sentiments

def analyze_review_sentiments(text):
    request_url = sentiment_analyzer_url+"analyze/"+text
    try:
        response = requests.get(request_url)
        return response.json()
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        print("Network exception occurred")
        return None

# def post_review(data_dict):
# Add code for posting review

def post_review(data_dict):
    print("=" * 50)
    print("POST_REVIEW FUNCTION CALLED!")
    print("=" * 50)
    request_url = backend_url+"/insert_review"
    print(f"=== POST REVIEW ===")
    print(f"Request URL: {request_url}")
    print(f"Backend URL: {backend_url}")
    print(f"Data being sent: {json.dumps(data_dict, indent=2)}")
    try:
        response = requests.post(request_url, json=data_dict)
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        return response.json()
    except Exception as e:
        print(f"ERROR in post_review: {e}")
        import traceback
        traceback.print_exc()
        return None