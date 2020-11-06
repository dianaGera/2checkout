from django.db import migrations
from accounts.models import MyUser;


def superuser_create(apps, schema_editor):
    MyUser.objects.create_superuser('admin@admin.com', 'admin')


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_myuser_address'),
    ]

    operations = [
        migrations.RunPython(superuser_create)
    ]