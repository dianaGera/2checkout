# Generated by Django 3.1 on 2022-02-09 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='myuser',
            name='applied_trial',
            field=models.BooleanField(default=False),
        ),
    ]