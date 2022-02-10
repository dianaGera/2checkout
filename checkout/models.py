import datetime
from datetime import timedelta

from django.db import models
from creditcards.models import CardNumberField, CardExpiryField, SecurityCodeField
from accounts.models import MyUser
from .subscription import headers, extend_a_subscription
from django.core.exceptions import ValidationError


class Payment(models.Model):
    cc_number = CardNumberField('card number')
    cc_expiry = CardExpiryField('expiration date')
    cc_code = SecurityCodeField('security code')


class Plan(models.Model):
    name = models.CharField(max_length=255)
    price = models.FloatField()
    period = models.PositiveIntegerField("Term in month", blank=True)
    code = models.CharField(max_length=255)
    product_id = models.CharField(max_length=25)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Plan'
        verbose_name_plural = 'Plans'

    def get_items(self):
        return self.items.all()


class Coupon(models.Model):
    coupon = models.CharField(max_length=50)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.coupon} {self.active}'


def allPlans():
    plans_list = Plan.objects.all().only('pk')
    return plans_list


class Promotion(models.Model):
    C_SINGLE = 0
    C_MULTIPLE = 1
    C_CHOICES = (
        (C_SINGLE, 'Single'),
        (C_MULTIPLE, 'Multiple')
    )
    D_FIXED = 0
    D_PERCENT = 1
    D_CHOICES = (
        (D_FIXED, 'Fixed'),
        (D_PERCENT, 'Percent')
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    code = models.CharField(max_length=50, null=True)
    discount_type = models.PositiveIntegerField(choices=D_CHOICES, default=1)
    discount_value = models.IntegerField()
    currency = models.CharField(max_length=50, default='USD', null=True)
    cycles = models.IntegerField(
        blank=True, default=1, help_text=
        '''
            How many subscription cycles will the coupon last for?
        '''
    )
    products = models.ManyToManyField(Plan, default=allPlans)
    start_day = models.DateField(
        blank=True, null=True, help_text=
        '''
            Starting date. The date when you set the promotion to start.
            Is NULL for promotions that start immediately after they are
            created.
        '''
    )
    end_day = models.DateField(
        blank=True, null=True, help_text=
        '''
            Ending date. The date when you set the promotion to end. Is
            NULL for promotions that you want active indefinitely.
        '''
    )
    coupon_type = models.PositiveIntegerField(
        choices=C_CHOICES, default=0, null=True, blank=True, help_text=
        '''
            SINGLE = one coupon code shared by all shoppers
            MULTIPLE = array of unique coupon codes, each designed for individual use
        '''
    )
    coupon_code = models.ManyToManyField(
        Coupon, blank=True, help_text=
        '''
            Codes = ['code1', 'code2']; ONLY when Type = 'MULTIPLE';
        '''
    )
    instant_discount = models.BooleanField(
        default=False, help_text=
        '''
            Selecting the instant discount option will auto-apply
            the discount for ALL the selected products for all shoppers,
            without the need to enter the discount coupon.
        '''
    )
    enable = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class PlanItem(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Plan item'
        verbose_name_plural = 'Plan items'


class Subscription(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE, related_name='subscription', null=True, blank=True)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    subscription_code = models.CharField(max_length=10, null=False, blank=False)
    start_date = models.DateField(null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)
    auto_update = models.BooleanField(default=True)
    extend = models.DateField(null=True, blank=True,
                              help_text="Enter the date of purchase", )

    promotion = models.ForeignKey(Promotion, null=True, on_delete=models.SET_NULL, blank=True)
    promotion_start_date = models.DateField(blank=True, null=True)

    def clean(self, *args, **kwargs):
        if self.extend < self.expiration_date:
            raise ValidationError('Please choose a future expiration date (or today).')
        super(Subscription, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        try:
            if self.extend > self.expiration_date:
                date_before_change = self.expiration_date
                self.expiration_date = self.extend

                subscription_identifier = self.user.subscription.subscription_code
                days = (self.expiration_date - date_before_change).days
                extend_a_subscription(headers, subscription_identifier, days)
        except:
            self.extend = self.expiration_date

        self.extend = self.expiration_date
        super(Subscription, self).save(*args, **kwargs)

    def __str__(self):
        return '{} - {}'.format(self.user, self.plan)

    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
