from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from checkout.subscription import headers, extend_a_subscription
from django.core.exceptions import ValidationError
from checkout.models import Promotion, Plan


class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email)
        )

        user.set_password(password)  # шифровка пароля
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    first_name = models.CharField("First name", max_length=150, blank=True)
    last_name = models.CharField("Last name", max_length=150, blank=True)
    country = models.CharField("Country", max_length=30, blank=True)
    city = models.CharField("City", max_length=30, blank=True)
    address = models.CharField("address", max_length=30, blank=True)
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    customer_reference = models.CharField(max_length=20, null=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    send_email = models.BooleanField(default=True)

    applied_trial = models.BooleanField(default=False)
    active_promotions = models.ManyToManyField(Promotion, blank=True)

    total_payment = models.FloatField(default=0)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


class Subscription(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE, related_name='subscription', null=True, blank=True)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    subscription_code = models.CharField(max_length=10, null=False, blank=False)
    start_date = models.DateField(null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)
    auto_update = models.BooleanField(default=True)
    extend = models.DateField(null=True, blank=True,
                              help_text="Enter the date of purchase", )

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