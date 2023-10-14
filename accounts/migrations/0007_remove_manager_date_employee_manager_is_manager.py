# Generated by Django 4.2.3 on 2023-07-17 18:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_alter_customuser_city_alter_customuser_health_center_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='manager',
            name='date_employee',
        ),
        migrations.AddField(
            model_name='manager',
            name='is_manager',
            field=models.BooleanField(default=False),
        ),
    ]
