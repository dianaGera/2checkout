# Generated by Django 3.1 on 2022-02-11 09:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('checkout', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='First name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='Last name')),
                ('country', models.CharField(blank=True, max_length=30, verbose_name='Country')),
                ('city', models.CharField(blank=True, max_length=30, verbose_name='City')),
                ('address', models.CharField(blank=True, max_length=30, verbose_name='address')),
                ('email', models.EmailField(max_length=255, unique=True, verbose_name='email address')),
                ('customer_reference', models.CharField(max_length=20, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('send_email', models.BooleanField(default=True)),
                ('applied_trial', models.BooleanField(default=False)),
                ('total_payment', models.FloatField(default=0)),
                ('active_promotions', models.ManyToManyField(blank=True, to='checkout.Promotion')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subscription_code', models.CharField(max_length=10)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('expiration_date', models.DateField(blank=True, null=True)),
                ('auto_update', models.BooleanField(default=True)),
                ('extend', models.DateField(blank=True, help_text='Enter the date of purchase', null=True)),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='checkout.plan')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subscription', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Subscription',
                'verbose_name_plural': 'Subscriptions',
            },
        ),
    ]
