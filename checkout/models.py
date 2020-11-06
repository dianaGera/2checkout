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
    period = models.CharField(max_length=15, blank=True)
    code = models.CharField(max_length=255)
    product_id = models.CharField(max_length=25)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Plan'
        verbose_name_plural = 'Plans'

    def get_items(self):
        return self.items.all()



class Promotion_fixed(models.Model):
    # title = models.CharField(max_length=255)
    # description = models.TextField()
    value = models.FloatField(null=True, blank=True)
    currency = models.CharField(max_length=10, null=True, blank=True)
    # cycles = models.IntegerField()

    # def __str__(self):
    #     return self.title

    class Meta:
        abstract = True

class Promotion_percent(models.Model):
    percent = models.CharField(max_length=10, null=True, blank=True)


    class Meta:
        abstract = True


class Promotion(Promotion_percent, Promotion_fixed):
    title = models.CharField(max_length=255)
    description = models.TextField()
    cycles = models.IntegerField()
    code = models.CharField(max_length=15, null=True, blank=True)

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
    start_date = models.DateField(auto_now_add=True, null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)
    auto_update = models.BooleanField(default=True)
    extend = models.DateField(null=True, blank=True,
                              help_text="Enter the date of purchase", )
    trial = models.BooleanField(default=False)

    promotion = models.ForeignKey(Promotion, null=True, on_delete=models.SET_NULL, blank=True)


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

    


