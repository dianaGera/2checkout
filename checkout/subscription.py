import os
import hmac
import hashlib
from time import gmtime, strftime
import time
import urllib.request
import requests
from ast import literal_eval
import json


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
    # r = requests.post('https://api.2checkout.com/rest/6.0/subscriptions/', headers=headers, data=data)
    r = urllib.request.Request('https://api.2checkout.com/rest/6.0/subscriptions/', headers=headers, data=data)
    print(r.__dict__)
    with urllib.request.urlopen(r) as response:
        resp = response.read()
    return resp.decode('utf-8').replace("\"", '')


def delete_subscription(headers, subscription_code):
    headers = headers()
    return requests.delete(f'https://api.2checkout.com/rest/6.0/subscriptions/{subscription_code}/', headers=headers)


def search_subscriptions(headers, email):
    r = requests.get('https://api.2checkout.com/rest/6.0/subscriptions/', headers=headers, params={'Email':'{}'.format(email)})
    subscription_info = r.text
    subscription_info = dict(literal_eval(subscription_info.replace('true', '\"true\"').replace('false', '\"false\"').replace('null', '\"null\"')))

    return subscription_info


def get_renewal_link(subscription_code):
    """ Retrieve the manual renewal link and the recurring billing status for a subscription. """
    header = headers()
    request_url = f'https://api.2checkout.com/rest/6.0/subscriptions/{subscription_code}/renewal/'
    response = requests.get(request_url, headers=header)
    return print('get_renewal_link', response.__dict__)


def stop_subscription(header, subscription_identifier):
    """Остановить автоматическое продление подписки"""
    request_url = 'https://api.2checkout.com/rest/6.0/subscriptions/{}/renewal/'.format(subscription_identifier)

    headers = header()
    requests.delete(request_url, headers=headers)
    # print(req.__dict__)

    # req = urllib.request.Request(request_url, headers=headers, method="DELETE")
    # with urllib.request.urlopen(req) as response:
    #     response = response.read()
    #     return response.decode('utf-8').replace("\"", '')
    #     print(response.decode())


def enable_subscription(header, subscription_identifier):
    """Возобновить автоматическое продление подписки"""

    """PUT: метод позволит продлить подписку контролируя цену и количество дней
    {
      "Currency": "usd",
      "Days": 15,
      "Price": 22.11
    }
    """
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
    """Set custom renewal prices for subscriptions and control the number of recurring billing cycles the price impact subscribers."""
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
    return response.status_code


def get_subscription_information(subscription_code):
    """GET: get information about subscription
       PUT: update info
       POST: enable subscription
       DELETE"""
    header = headers()
    request_url = f'https://api.2checkout.com/rest/6.0/subscriptions/{subscription_code}'
    response = requests.get(request_url, headers=header)
    return print("get_subscription_information", response.__dict__)


def get_subscription_customer(subscription_code):
    """GET: get customer information by subscription code

       POST: assign subscription to another customer with data
        {
          "ExternalCustomerReference": "ThisIsTheCustomerID123",
          "AvangateCustomerReference": 23423543543
        }
       """

    header = headers()
    request_url = f'https://api.2checkout.com/rest/6.0/subscriptions/{subscription_code}/customer/'
    response = requests.get(request_url, headers=header)
    return print('get_subscription_customer', response.__dict__)


def get_subscription_history(subscription_code):
    header = headers()
    request_url = f'https://api.2checkout.com/rest/6.0/subscriptions/{subscription_code}/history/'
    response = requests.get(request_url, headers=header)
    return print('get_subscription_history', response.__dict__)


def turn_on_notifications(subscription_code):
    """Subscribe shoppers to subscription renewal notifications.
    By default, all notifications is turned on"""
    header = headers()
    request_url = f'https://api.2checkout.com/rest/6.0/subscriptions/{subscription_code}/notification/'
    response = requests.post(request_url, headers=header)
    return print('get_subscription_history', response)


def turn_off_notifications(subscription_code):
    """Disable subscription renewal notifications for a specific subscription."""
    header = headers()
    request_url = f'https://api.2checkout.com/rest/6.0/subscriptions/{subscription_code}/notification/'
    response = requests.delete(request_url, headers=header)
    return print('get_subscription_history', response.__dict__)


def get_subscription_next_renewal_price(subscription_code, currency):
    """Retrieve pricing details for the next charge necessary to renew a specific subscription."""
    header = headers()
    request_url = f'https://api.2checkout.com/rest/6.0/subscriptions/{subscription_code}/renewal/price/{currency}/'
    response = requests.get(request_url, headers=header)
    return print('get_subscription_next_renewal_price', response.__dict__)


def get_all_promotions_for_product(product_code):
    """Get all promotions set for single product"""
    header = headers()
    request_url = f'https://api.2checkout.com/rest/6.0/products/{product_code}/promotions/'
    response = requests.get(request_url, headers=header)
    return print('get_all_promotions', response.__dict__)


def get_all_active_promotions():
    """Get all active promotions"""
    header = headers()
    request_url = f'https://api.2checkout.com/rest/6.0/promotions/'
    response = requests.get(request_url, headers=header)
    return print('get_all_active_promotions', response.__dict__)


def create_promotion(data):
    """Create promotion"""
    header = headers()
    data = str(data).replace('None', 'null').replace('\'', "\"").encode("utf-8")
    request_url = f'https://api.2checkout.com/rest/6.0/promotions/'
    response = requests.post(request_url, headers=header, data=data)
    return print('get_all_active_promotions', response)


# disable
def get_customer_next_renewal_price(subscription_code, currency):
    """Retrieve next price for subscription"""
    header = headers()
    request_url = f'https://api.2checkout.com/rest/6.0/subscription/{subscription_code}/renewal/price/{currency}/'
    response = requests.get(request_url, headers=header)
    return print('get_all_active_promotions', response, response.__dict__)


promotion = {
    "Type": "REGULAR",
    "ApplyRecurring": None,
    "ChannelType": "ECOMMERCE",
    "Coupon": {
        "Codes": [
            "code1",
            "code2"
        ],
        "Type": "MULTIPLE"
    },
    "Description": "Promo description1",
    "Discount": {
        "Type": "PERCENT",
        "Value": 41
    },
    "Enabled": True,
    "EndDate": None,
    "InstantDiscount": 0,
    "MaximumOrdersNumber": None,
    "MaximumQuantity": None,
    "Name": "Promo percentage REST",
    "Products": [
        {
            "Code": "my_subscription_1"
        }
    ],
    "PublishToAffiliatesNetwork": 0,
    "StartDate": None
}