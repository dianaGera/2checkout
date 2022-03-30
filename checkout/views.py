import os
import hmac
import hashlib
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from creditcards import types
from .models import Plan, Promotion, Coupon
from .forms import PaymentForm
from .data import data, payment_data, checkout_js
from .subscription import headers, add_subscription, stop_subscription, enable_subscription, apply_coupon, \
    get_subscription_information, headers, create_orders
from accounts.models import MyUser, Subscription


def subscription_form(request, form, plan, price, start_date=None):
    cc_number = form.cleaned_data.get('cc_number')
    cc_expiry = str(form.cleaned_data.get('cc_expiry')).split('-')
    cc_code = form.cleaned_data.get('cc_code')
    for i in types.CC_TYPES:
        if i[0] == types.get_type(cc_number):
            cc_type = i[1]['title']

    data['Payment']['CardNumber'] = cc_number
    data['Payment']['ExpirationYear'] = cc_expiry[0]
    data['Payment']['ExpirationMonth'] = cc_expiry[1]
    data['Payment']['CardType'] = cc_type
    data['Payment']['CCID'] = cc_code

    if not start_date:
        start_date = datetime.now()
    date_end = start_date + relativedelta(months=+plan.period)
    # start_date = datetime.now() - timedelta(days=30)
    # if plan.period == 'week':
    #     date += timedelta(days=7)
    # elif plan.period == 'month':
    #     days_in_month = calendar.monthrange(date.year, date.month)[1]
    #     date += timedelta(days=days_in_month)
    # else:
    #     date = date.today() + relativedelta(months=+6)

    data['SubscriptionValue'] = price
    data['NextRenewalPrice'] = plan.price
    data['StartDate'] = start_date.strftime("%Y-%m-%d").replace('\'', "\"")

    data['ExpirationDate'] = date_end.strftime("%Y-%m-%d").replace('\'', "\"")
    data['ExternalSubscriptionReference'] = request.user.customer_reference

    data['Product']['ProductCode'] = plan.code
    data['Product']['ProductId'] = plan.product_id
    data['Product']['ProductName'] = plan.name

    data['EndUser']['Address1'] = request.user.address
    data['EndUser']['City'] = request.user.city
    data['EndUser']['Email'] = request.user.email
    data['EndUser']['FirstName'] = request.user.first_name
    data['EndUser']['LastName'] = request.user.last_name
    data['EndUser']['CustomerReference'] = request.user.customer_reference
    return data


def payment_form(request, form, plan, price, start_date=None):
    cc_number = form.cleaned_data.get('cc_number')
    cc_expiry = str(form.cleaned_data.get('cc_expiry')).split('-')
    cc_code = form.cleaned_data.get('cc_code')
    for i in types.CC_TYPES:
        if i[0] == types.get_type(cc_number):
            if i[1]['title'] == 'American Express':
                cc_type = 'AMEX'
            else:
                cc_type = i[1]['title']

    payment_data['BillingDetails']['Address1'] = request.user.address
    payment_data['BillingDetails']['City'] = request.user.city
    payment_data['BillingDetails']['Email'] = request.user.email
    payment_data['BillingDetails']['FirstName'] = request.user.first_name
    payment_data['BillingDetails']['LastName'] = request.user.last_name

    payment_data['Items'][0]['Code'] = plan.code

    payment_data['PaymentDetails']['PaymentMethod']['CCID'] = cc_code
    payment_data['PaymentDetails']['PaymentMethod']['CardNumber'] = cc_number
    payment_data['PaymentDetails']['PaymentMethod']['CardType'] = cc_type
    payment_data['PaymentDetails']['PaymentMethod']['ExpirationMonth'] = cc_expiry[1]
    payment_data['PaymentDetails']['PaymentMethod']['ExpirationYear'] = cc_expiry[0]
    payment_data['PaymentDetails']['PaymentMethod']['HolderName'] = f'{request.user.first_name} {request.user.last_name}'
    
    return payment_data


def coupon_discount_value(coupon, plan):
    
    if coupon.discount_type == Promotion.D_FIXED:
        price = plan.price - coupon.discount_value
        if price < 0:
            price = 0
    else:
        percent = coupon.discount_value
        price = plan.price - ((plan.price * percent) / 100)
    return price


@login_required()
def subscription_api(request):
    # print(headers())
    # create_orders()
    plans = Plan.objects.all().order_by('pk')
    user = MyUser.objects.get(customer_reference=request.user.customer_reference)
    promotions = Promotion.objects.filter(coupon_type=Promotion.C_SINGLE).exclude(
                                          id__in=user.active_promotions.all())
    context = dict()
    if request.method == 'POST':
        # if user want to switch to another subscription,
        # then displays confirmation page with remnant computation
        if request.POST.get("subscription"):
            user_data = request.user.subscription
            change_to = plans.get(pk=request.POST.get("subscription"))

            day_pass = (datetime.now().date() - user_data.start_date).days
            day_left = (user_data.expiration_date - datetime.now().date()).days
            period = (user_data.expiration_date - user_data.start_date).days

            price_per_day_first = user_data.plan.price / int(period)
            price_per_day_second = change_to.price / int(period)
            if user.total_payment > 0:
                remnant = "%.2f" % (change_to.price - (user_data.plan.price - day_pass * price_per_day_first))
                remnant_to_pay = remnant if float(remnant) > 0 else 0
            else:
                remnant_to_pay = change_to.price

            request.session['remnant_to_pay'] = remnant_to_pay
            request.session['change_to'] = change_to.pk

            context = {
                'prise': remnant_to_pay,
                'change_to': change_to
            }
            return render(request, 'checkout/change_subscription.html', context=context)

        # if user want to apply coupon
        if request.POST.get('coupon'):
            try:
                promotion = Promotion.objects.exclude(id__in=user.active_promotions.all()).filter(
                    Q(Q(coupon_code__coupon=request.POST.get('coupon')) &
                      Q(coupon_code__active=True)) |
                    Q(Q(code=request.POST.get('coupon')) &
                      Q(enable=True) & ~
                      Q(coupon_type=1))
                ).first()

                context = {
                    'promotion': promotion,
                    'subscription': request.user.subscription.pk,
                    'plan': request.user.subscription.plan
                }
                if promotion.code != request.POST.get('coupon'):
                    context.update({
                            'coupon': request.POST.get('coupon')
                            if int(promotion.coupon_type) == Promotion.C_MULTIPLE else None
                        })
                return render(request, 'includes/apply_coupon.html', context=context)

            except Exception as _ex:
                messages.add_message(request, messages.INFO, 'Not Found')
    context = {
        'plans': plans,
        'promotions': promotions,
        'basic': plans[1:5],
        'standard': plans[5:9],
        'premium': plans[9:13]
        }
    return render(request, 'checkout/subscription_api.html', context=context)


def subscription_service(request):
    SECRET_KEY_CHECKOUT = os.getenv('SECRET_KEY_CHECKOUT')
    if request.user.is_authenticated:
        plans = Plan.objects.all().order_by('pk')
        promotions = Promotion.objects.all()

        SIGNATURE_SECRET_WORD = os.getenv('SIGNATURE_SECRET_WORD')

        msg = str(len('' + str(request.user.id))) + '' + str(request.user.id)
        signature = hmac.new(bytes(SIGNATURE_SECRET_WORD, encoding='utf-8'), bytes(msg, encoding='utf-8'),
                             digestmod=hashlib.sha256).hexdigest()

        hash_dict = {}
        for plan in plans:
            link = "PRODS={1}&QTY=1&PRICES{1}[USD]=0&TPERIOD=7".format(plan.product_id, plan.product_id)
            link_hash = str(len(link)) + link
            hash = hmac.new(bytes(SECRET_KEY_CHECKOUT, encoding='utf-8'), bytes(link_hash, encoding='utf-8'),
                            digestmod=hashlib.md5).hexdigest()
            hash_dict[plan.name] = link + "&PHASH=" + hash
        context = {
            'plans': plans,
            'signature': signature,
            'hash_dict': hash_dict,
            'promotions': promotions}
        return render(request, 'checkout/subscription_service.html', context=context)
    else:
        return redirect('accounts:login')



# Apply payment with 2Pay.js token
@csrf_exempt
@login_required
def checkout(request, pk):
    plan = Plan.objects.get(id=pk)
    if request.method == 'POST' and request.is_ajax():
        token = json.loads(request.body.decode('UTF-8'))
        print(token['content'])
        
        checkout_js['PaymentDetails']['PaymentMethod']['EesToken'] = token['content']
        create_orders(headers, checkout_js)
        return HttpResponse(json.dumps({'token': token}), content_type="application/json")
    else:
        return render(request, 'checkout/check.html', {'plan': plan})


#Apply payment with using credit card data
@login_required
def checkout(request, pk):
    if not hasattr(request.user, 'subscription'):
        plan = Plan.objects.get(id=pk)
        if request.method == 'POST':
            form = PaymentForm(request.POST)

            if form.is_valid():
                # find coupon
                user = MyUser.objects.get(email=request.user.email)
                user_coupon = form['coupon'].value()
                if user_coupon != '':
                    user_promotion_list = MyUser.objects.get(
                        customer_reference=request.user.customer_reference
                    ).active_promotions.all()
                    coupon = Promotion.objects.exclude(id__in=user_promotion_list).filter(
                        Q(Q(coupon_code__coupon=user_coupon) &
                          Q(coupon_code__active=True)) |
                        Q(Q(code=user_coupon) &
                          Q(enable=True) & ~
                          Q(coupon_type=1))
                    ).first()
                else:
                    coupon = None

                # change enroll day if user applied trial period at first time
                start_date = datetime.now()
                price = plan.price

                if form['trial'].value():
                    start_date = datetime.now() + timedelta(days=7) - relativedelta(months=+plan.period)
                    price = 0
                    form_data = payment_form(request, form, plan, price, start_date)
                # if user what to subscribe with promotion
                else:
                    if coupon:
                        price = coupon_discount_value(coupon, plan)
                    form_data = payment_form(request, form, plan, price, start_date)

                subscription_code = create_orders(headers, form_data)
                user.total_payment += price
                user.save()

                # apply coupon discount for next billing period if it is
                if coupon:
                    price = coupon_discount_value(coupon, plan)
                    coupon_cycles = int(coupon.cycles) - 1 if int(coupon.cycles) - 1 > 0 else None
                    if coupon_cycles:
                        if request.user.applied_trial:
                            coupon_cycles -= 1
                        else:
                            coupon_cycles += 1
                    else:
                        coupon_cycles = 0
                    apply_coupon(
                        headers, subscription_code, coupon.currency,
                        coupon_cycles, coupon.description, price
                    )
                    # deactivate coupon
                    if int(coupon.coupon_type) == Promotion.C_MULTIPLE:
                        coupon = Coupon.objects.get(coupon=form['coupon'].value())
                        coupon.active = False
                        coupon.save()
                    else:
                        request.user.active_promotions.add(coupon.pk)

                # add subscription to database
                # Subscription.objects.create(
                #     user=request.user,
                #     plan=plan,
                #     subscription_code=subscription_code,
                #     expiration_date=form_data['ExpirationDate'],
                #     start_date=form_data['StartDate']
                # )
                # # deactivate trial
                # if not user.applied_trial:
                #     user.applied_trial = True
                #     user.save()

                return redirect('subscription_api')
        else:
            form = PaymentForm()
    else:
        return redirect('subscription_api')

    return render(request, 'checkout/check.html', {'plan': plan, 'form': form})


def change_subscription(request):
    change_to = Plan.objects.get(pk=request.session.get('change_to'))
    remnant_to_pay = request.session.get('remnant_to_pay')

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            data = subscription_form(request, form, change_to, price=remnant_to_pay)
            # data['SubscriptionValue'] = remnant_to_pay
            # data['StartDate'] = request.user.subscription.start_date.strftime("%Y-%m-%d").replace('\'', "\"")
            # data['ExpirationDate'] = request.user.subscription.expiration_date.strftime("%Y-%m-%d").replace('\'', "\"")
            # data['Product']['ProductCode'] = change_to.product_id
            # delete = delete_subscription(headers, request.user.subscription.subscription_code)
            # print(delete.status_code)
            # if delete.status_code == 200:
            Subscription.objects.get(subscription_code=request.user.subscription.subscription_code).delete()
            subscription_code = add_subscription(headers, data)
            Subscription.objects.create(
                user=request.user,
                plan=change_to,
                subscription_code=subscription_code,
                expiration_date=data['ExpirationDate'],
                start_date=data['StartDate']
            )
            request.user.total_payment += float(remnant_to_pay)
            request.user.save()
        return redirect('subscription_api')
    else:
        form = PaymentForm()
    return render(request, 'checkout/check.html', {'form': form})


def promotion_cod(request):
    coupon_codes = {}

    for coupon_code in Promotion.objects.all():
        if coupon_code.code:
            if coupon_code.discount_value:
                coupon_codes[coupon_code.code] = coupon_code.discount_value
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

        if coupon.discount_type == Promotion.D_FIXED:
            price = subscription.plan.price - coupon.discount_value
            if price < 0:
                price = 0
        else:
            percent = coupon.discount_value
            price = subscription.plan.price - ((subscription.plan.price * percent) / 100)

        response = apply_coupon(headers, subscription.subscription_code, currency, cycles, text, price)
        if response == 200:
            subscription.promotion = coupon
            subscription.save()
            if request.POST.get('coupon'):
                coupon = Coupon.objects.get(coupon=request.POST.get('coupon'))
                coupon.active = False
                coupon.save()

        return redirect('subscription_api')
    return HttpResponse(status=200)


@csrf_exempt
def create_order(request):
    """ Create subscription locally if it was successfully paid """
    # Accept IPN connection
    if request.method == "GET":
        return HttpResponse("OK")

    SECRET_KEY_CHECKOUT = os.getenv('SECRET_KEY_CHECKOUT')
    EXTERNAL_CUSTOMER_REFERENCE = request.POST.get('EXTERNAL_CUSTOMER_REFERENCE')       # returns None
    IPN_LICENSE_REF = request.POST.get('IPN_LICENSE_REF[]')
    IPN_PID = request.POST.get('IPN_PID[]')
    IPN_PNAME = request.POST.get('IPN_PNAME[]')
    IPN_DATE = request.POST.get('IPN_DATE')
    IPN_TOTALGENERAL = request.POST.get('IPN_TOTALGENERAL')         # total payment price
    MESSAGE_TYPE = request.POST.get('MESSAGE_TYPE')
    IPN_PRICE = request.POST.get('IPN_PRICE[]')
    CUSTOMEREMAIL = request.POST.get('CUSTOMEREMAIL')
    ORDERSTATUS = request.POST.get('ORDERSTATUS')

    # plan = Plan.objects.get(product_id=IPN_LICENSE_PROD)
    # user = MyUser.objects.get(id=EXTERNAL_CUSTOMER_REFERENCE)
    print(IPN_LICENSE_REF, 'SUB ID')
    print(IPN_PRICE, 'price')
    print(CUSTOMEREMAIL, 'CUSTOMEREMAIL')
    print(ORDERSTATUS, 'ORDERSTATUS')                 # returns None
    print(IPN_TOTALGENERAL, 'IPN_TOTALGENERAL')
    print(MESSAGE_TYPE, 'MESSAGE_TYPE')

    # if ORDERSTATUS == 'COMPLETE':
    #     user = MyUser.objects.get(email=CUSTOMEREMAIL)
    #     plan = Plan.objects.get(product_id=IPN_PID)
    #     Subscription.objects.create(
    #         user=user,
    #         plan=plan,
    #         subscription_code=IPN_LICENSE_REF,
    #         expiration_date=data['ExpirationDate'],     #TODO
    #         start_date=data['StartDate']
    #     )
    # else:
    #     pass
    # date = datetime.now()
    # date += timedelta(days=7)
    #
    # if not Subscription.objects.filter(user=user).exists() and IPN_LICENSE_REF != '':
    #     if plan and user:
    #         Subscription.objects.create(user=user, plan=plan, subscription_code=IPN_LICENSE_REF,
    #                                     expiration_date=date.strftime("%Y-%m-%d"), trial=True)
    #
    DATE = datetime.now().strftime("%Y%m%d%H%M%S")
    msg_response = str(len(IPN_PID)) + IPN_PID + str(len(IPN_PNAME)) + IPN_PNAME + str(len(IPN_DATE)) + IPN_DATE + str(
        len(DATE)) + DATE
    hash_resp = hmac.new(bytes(SECRET_KEY_CHECKOUT, encoding='utf-8'), bytes(msg_response, encoding='utf-8'),
                         digestmod=hashlib.md5).hexdigest()
    print('some print', f"<EPAYMENT>{DATE}|{hash_resp}</EPAYMENT>")
    return HttpResponse(f"<EPAYMENT>{DATE}|{hash_resp}</EPAYMENT>")




