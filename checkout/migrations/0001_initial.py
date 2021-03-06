# Generated by Django 3.1 on 2022-02-11 09:59

import checkout.models
import creditcards.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coupon', models.CharField(max_length=50)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cc_number', creditcards.models.CardNumberField(max_length=25, verbose_name='card number')),
                ('cc_expiry', creditcards.models.CardExpiryField(verbose_name='expiration date')),
                ('cc_code', creditcards.models.SecurityCodeField(max_length=4, verbose_name='security code')),
            ],
        ),
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('price', models.FloatField()),
                ('period', models.PositiveIntegerField(blank=True, verbose_name='Term in month')),
                ('code', models.CharField(max_length=255)),
                ('product_id', models.CharField(max_length=25)),
            ],
            options={
                'verbose_name': 'Plan',
                'verbose_name_plural': 'Plans',
            },
        ),
        migrations.CreateModel(
            name='Promotion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('code', models.CharField(max_length=50, null=True)),
                ('discount_type', models.PositiveIntegerField(choices=[(0, 'Fixed'), (1, 'Percent')], default=1)),
                ('discount_value', models.IntegerField()),
                ('currency', models.CharField(default='USD', max_length=50, null=True)),
                ('cycles', models.IntegerField(blank=True, default=1, help_text='\n            How many subscription cycles will the coupon last for?\n        ')),
                ('start_day', models.DateField(blank=True, help_text='\n            Starting date. The date when you set the promotion to start.\n            Is NULL for promotions that start immediately after they are\n            created.\n        ', null=True)),
                ('end_day', models.DateField(blank=True, help_text='\n            Ending date. The date when you set the promotion to end. Is\n            NULL for promotions that you want active indefinitely.\n        ', null=True)),
                ('coupon_type', models.PositiveIntegerField(blank=True, choices=[(0, 'Single'), (1, 'Multiple')], default=0, help_text='\n            SINGLE = one coupon code shared by all shoppers\n            MULTIPLE = array of unique coupon codes, each designed for individual use\n        ', null=True)),
                ('instant_discount', models.BooleanField(default=False, help_text='\n            Selecting the instant discount option will auto-apply\n            the discount for ALL the selected products for all shoppers,\n            without the need to enter the discount coupon.\n        ')),
                ('enable', models.BooleanField(default=True)),
                ('coupon_code', models.ManyToManyField(blank=True, help_text="\n            Codes = ['code1', 'code2']; ONLY when Type = 'MULTIPLE';\n        ", to='checkout.Coupon')),
                ('products', models.ManyToManyField(default=checkout.models.allPlans, to='checkout.Plan')),
            ],
        ),
        migrations.CreateModel(
            name='PlanItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='checkout.plan')),
            ],
            options={
                'verbose_name': 'Plan item',
                'verbose_name_plural': 'Plan items',
            },
        ),
    ]
