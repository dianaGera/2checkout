import os
from datetime import datetime
import hmac
import hashlib
from time import gmtime, strftime
import time
import urllib.request
import requests
from ast import literal_eval
import os
import requests
import json


data = {
    "AdditionalInfo": None,
    "CustomPriceBillingCyclesLeft": 1,
    "DeliveryInfo": {
        "Codes": [
            {
                "Code": "___TEST___CODE____",
                "Description": None,
                "ExtraInfo": None,
                "File": None
            }
        ],
        "Description": None
    },
    "EndUser": {
        "Address1": "Test Address",
        "Address2": "",
        "City": "",
        "Company": "",
        "CountryCode": "us",
        "Email": "customer@2Checkout.com",
        "Fax": "",
        "FirstName": "Customer",
        "Language": "",
        "LastName": "2Checkout",
        "Phone": "",
        "State": "CA",
        "Zip": "12345"
    },
    "ExpirationDate": "",
    "ExternalCustomerReference": None,
    "ExternalSubscriptionReference": "ThisIsYourUniqueIdentifier123",
    "NextRenewalPrice": 0,
    "NextRenewalPriceCurrency": "usd",
    "PartnerCode": "",
    "Payment": {
        "CCID": "",
        "CardNumber": "",
        "CardType": "",
        "ExpirationMonth": "",
        "ExpirationYear": "",
        "HolderName": ""
    },
    "Product": {
        "PriceOptionCodes": [
            ""
        ],
        "ProductCode": "",
        "ProductId": "",
        "ProductName": "",
        "ProductQuantity": 1,
        "ProductVersion": ""
    },
    "StartDate": "",
    "SubscriptionValue": 0,
    "SubscriptionValueCurrency": "usd",
    "Test": 1
}


def headers():
    SECRET_KEY_CHECKOUT = os.getenv('SECRET_KEY_CHECKOUT')
    VENDOR_CODE = os.getenv('VENDOR_CODE')

    REQUEST_DATE_TIME = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

    msg_response = str(len(VENDOR_CODE)) + VENDOR_CODE + str(len(REQUEST_DATE_TIME)) + REQUEST_DATE_TIME

    HASH = hmac.new(bytes(SECRET_KEY_CHECKOUT, encoding='utf-8'), bytes(msg_response, encoding='utf-8'), digestmod=hashlib.md5).hexdigest()

    Authentication = 'code="{}" date="{}" hash="{}"'.format(VENDOR_CODE, REQUEST_DATE_TIME, HASH)

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Avangate-Authentication': Authentication
    }

    return headers


def add_subscription(headers, data):
    headers = headers()

    data = str(data).replace('None', 'null').replace('\'', "\"").encode("utf-8")
    r = urllib.request.Request('https://api.2checkout.com/rest/6.0/subscriptions/', headers=headers, data=data)

    with urllib.request.urlopen(r) as response:
        resp = response.read()
    return resp.decode('utf-8').replace("\"", '')


def search_subscriptions(headers, email):
    r = requests.get('https://api.2checkout.com/rest/6.0/subscriptions/', headers=headers, params={'Email':'{}'.format(email)})

    subscription_info = r.text
    subscription_info = dict(literal_eval(subscription_info.replace('true', '\"true\"').replace('false', '\"false\"').replace('null', '\"null\"')))

    return subscription_info


def get_info_about_subscription(headers, subscription_code):
    headers = headers()

    r = urllib.request.Request('https://api.2checkout.com/rest/6.0/subscriptions/{}/'.format(subscription_code),
                               headers=headers, method='GET')

    with urllib.request.urlopen(r) as response:
        resp = response.read()
        print(resp.decode())


def stop_subscription(header, subscription_identifier):
    request_url = 'https://api.2checkout.com/rest/6.0/subscriptions/{}/renewal/'.format(subscription_identifier)

    headers = header()

    req = urllib.request.Request(request_url, headers=headers, method="DELETE")
    with urllib.request.urlopen(req) as response:
        response = response.read()
        print(response.decode())
    

def enable_subscription(header, subscription_identifier):
    """возобновить автоматическое продление подписки"""
    request_url = 'https://api.2checkout.com/rest/6.0/subscriptions/{}/renewal/'.format(subscription_identifier)
    headers = header()
    req = urllib.request.Request(request_url, headers=headers, method="POST")
    with urllib.request.urlopen(req) as response:
        response = response.read()
        print(response.decode())


def extend_a_subscription(header, subscription_identifier, days):
    """Продлить подписку"""

    request_url = 'https://api.2checkout.com/rest/6.0/subscriptions/{}/history/?Days={}'.format(subscription_identifier, days)

    headers = header()

    req = urllib.request.Request(request_url, headers=headers, method="PUT")

    with urllib.request.urlopen(req) as response:
        response = response.read()
        print(response.decode())



def apply_coupon(header, subscription_identifier, currency, cycles, text, price):
    request_url = f'https://api.2checkout.com/rest/6.0/subscriptions/{subscription_identifier}/renewal/price/{currency}/'

    data = {
        "Cycles": cycles,
        "Currency": currency,
        "Price": price,
        "Text": text
    }

    data = json.dumps(data)

    headers = header()
    response = requests.put(request_url, headers=headers, data=data)
    print(response.status_code)
    return response.status_code