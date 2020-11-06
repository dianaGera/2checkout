from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Plan, Subscription, Promotion
from .forms import PaymentForm
from creditcards import types
from .subscription import headers, add_subscription, data, stop_subscription, enable_subscription, apply_coupon
from datetime import datetime, timedelta
import calendar
from dateutil.relativedelta import relativedelta

from accounts.models import MyUser
 
from django.core import serializers
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model

import os
import hmac
import hashlib
from datetime import datetime
import requests
import json


def subscription_api(request):
    if request.user.is_authenticated:
        plans = Plan.objects.all()

        promotions = Promotion.objects.all()

        return render(request, 'checkout/subscription_api.html', {'plans': plans, 'promotions': promotions})
    else:
        return redirect('accounts:login')


def subscription_service(request):
    SECRET_KEY_CHECKOUT = os.getenv('SECRET_KEY_CHECKOUT')
    if request.user.is_authenticated:
        plans = Plan.objects.all()
        promotions = Promotion.objects.all()

        SIGNATURE_SECRET_WORD = os.getenv('SIGNATURE_SECRET_WORD')

        msg = str(len('' + str(request.user.id))) + '' + str(request.user.id)
        signature = hmac.new(bytes(SIGNATURE_SECRET_WORD, encoding='utf-8'), bytes(msg, encoding='utf-8'), digestmod=hashlib.sha256).hexdigest()

        hash_dict = {}
        for plan in plans:
            link = "PRODS={1}&QTY=1&PRICES{1}[USD]=0&TPERIOD=7".format(plan.product_id, plan.product_id)
            link_hash = str(len(link)) + link
            hash = hmac.new(bytes(SECRET_KEY_CHECKOUT, encoding='utf-8'), bytes(link_hash, encoding='utf-8'), digestmod=hashlib.md5).hexdigest()
            hash_dict[plan.name] = link + "&PHASH=" + hash


        return render(request, 'checkout/subscription_service.html', {'plans': plans, 'signature': signature, 'hash_dict': hash_dict, 'promotions': promotions})
    else:
        return redirect('accounts:login')


def checkout(request, pk):
    if request.user.is_authenticated:
        if not hasattr(request.user, 'subscription'):

            plan = Plan.objects.get(id=pk)

            if request.method == 'POST':
                form = PaymentForm(request.POST)

                if form.is_valid():
                    cc_number = form.cleaned_data.get('cc_number')
                    cc_expiry = str(form.cleaned_data.get('cc_expiry')).split('-')
                    cc_code = form.cleaned_data.get('cc_code')

                    new_price = request.POST.get('price')

                    for i in types.CC_TYPES:
                        if i[0] == types.get_type(cc_number):
                            cc_type = i[1]['title']

                    data['Payment']['CardNumber'] = cc_number
                    data['Payment']['ExpirationYear'] = cc_expiry[0]
                    data['Payment']['ExpirationMonth'] = cc_expiry[1]
                    data['Payment']['CardType'] = cc_type
                    data['Payment']['CCID'] = cc_code

                    data['SubscriptionValue'] = new_price
                    data['NextRenewalPrice'] = plan.price

                    date = datetime.now()
                    start_data = date
                    data['StartDate'] = date.strftime("%Y-%m-%d").replace('\'', "\"")

                    if plan.period == 'week':
                        date += timedelta(days=7)
                    elif plan.period == 'month':
                        days_in_month = calendar.monthrange(date.year, date.month)[1]
                        date += timedelta(days=days_in_month)
                    else:
                        date = date.today() + relativedelta(months=+6)

                    data['ExpirationDate'] = date.strftime("%Y-%m-%d").replace('\'', "\"")

                    data['Product']['ProductCode'] = plan.code
                    data['Product']['ProductId'] = plan.product_id
                    data['Product']['ProductName'] = plan.name

                    data['EndUser']['Address1'] = request.user.address
                    data['EndUser']['City'] = request.user.city
                    data['EndUser']['Email'] = request.user.email
                    data['EndUser']['FirstName'] = request.user.first_name
                    data['EndUser']['LastName'] = request.user.last_name

                    subscription_code = add_subscription(headers, data)

                    Subscription.objects.create(user=request.user, plan=plan, subscription_code=subscription_code,
                                                expiration_date=date.strftime("%Y-%m-%d"),
                                                start_date=start_data.strftime("%Y-%m-%d"))
                    return redirect('subscription_api')
            else:
                form = PaymentForm()
        else:
            return redirect('subscription_api')
    else:
        return redirect('accounts:login')

    return render(request, 'checkout/check.html', {'plan': plan, 'form': form})


def promotion_cod(request):
    coupon_codes = {}

    for coupon_code in Promotion.objects.all():
        if not coupon_code.code is None:
            if coupon_code.value:
                coupon_codes[coupon_code.code] = coupon_code.value
            else:
                coupon_codes[coupon_code.code] = coupon_code.percent

    response = json.dumps(coupon_codes)
    return HttpResponse(response, content_type='application/json') 


def stop_auto_subscription(request, pk):
    subscription = get_object_or_404(Subscription, pk=pk)

    if request.method == 'POST':
        stop_subscription(headers, subscription.subscription_code)

        subscription.auto_update = False
        subscription.save()

        return redirect('subscription_api')
    return HttpResponse(status=200)


def enable_auto_subscription(request, pk):
    subscription = get_object_or_404(Subscription, pk=pk)

    if request.method == 'POST':
        enable_subscription(headers, subscription.subscription_code)

        subscription.auto_update = True
        subscription.save()

        return redirect('subscription_api')
    return HttpResponse(status=200)


def apply_vouchers(request, pk, coupon_id):
    
    subscription = get_object_or_404(Subscription, pk=pk)
    coupon = get_object_or_404(Promotion, pk=coupon_id)
    if request.method == 'POST':
        currency = coupon.currency
        cycles = coupon.cycles
        text = coupon.description

        if coupon.value:
            price = subscription.plan.price - coupon.value
        else:
            percent = (coupon.percent).split(' ')[0]
            price = (subscription.plan.price * float(percent)) / 100

        response = apply_coupon(headers, subscription.subscription_code, currency, cycles, text, price)

        if response == 200:
            subscription.promotion = coupon
            subscription.save()
            
        return redirect('subscription_api')
    return HttpResponse(status=200)


@csrf_exempt
def create_order(request): 
    """ Create subscription locally if it was successfully paid """
    # Accept IPN connection
    if request.method == "GET":
        return HttpResponse("Connected")

    
    SECRET_KEY_CHECKOUT = os.getenv('SECRET_KEY_CHECKOUT')
    
    EXTERNAL_CUSTOMER_REFERENCE = request.POST.get('EXTERNAL_CUSTOMER_REFERENCE')
    IPN_LICENSE_REF = request.POST.get('IPN_LICENSE_REF[]')
    IPN_LICENSE_PROD = request.POST.get('IPN_LICENSE_PROD[]')
    IPN_PID = request.POST.get('IPN_PID[]')
    IPN_PNAME = request.POST.get('IPN_PNAME[]')
    IPN_DATE = request.POST.get('IPN_DATE')

    plan = Plan.objects.get(product_id=IPN_LICENSE_PROD)
    user = MyUser.objects.get(id=EXTERNAL_CUSTOMER_REFERENCE)

    date = datetime.now()
    date += timedelta(days=7)

    if not Subscription.objects.filter(user=user).exists() and IPN_LICENSE_REF != '': 
        if plan and user:
            Subscription.objects.create(user=user, plan=plan, subscription_code=IPN_LICENSE_REF, expiration_date=date.strftime("%Y-%m-%d"), trial=True)

    DATE = datetime.now().strftime("%Y%m%d%H%M%S")
    msg_response = str(len(IPN_PID)) + IPN_PID + str(len(IPN_PNAME)) + IPN_PNAME + str(len(IPN_DATE)) + IPN_DATE + str(len(DATE)) + DATE
    hash_resp = hmac.new(bytes(SECRET_KEY_CHECKOUT, encoding='utf-8'), bytes(msg_response, encoding='utf-8'), digestmod=hashlib.md5).hexdigest()
    return HttpResponse(f"<EPAYMENT>{DATE}|{hash_resp}</EPAYMENT>")
