# Generated by Django 4.2.3 on 2023-09-17 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('temps', '0004_deviceinformation'),
    ]

    operations = [
        migrations.AddField(
            model_name='deviceinformation',
            name='city',
            field=models.CharField(blank=True, default='مشهد', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='deviceinformation',
            name='health_center',
            field=models.CharField(blank=True, default='مشهد', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='deviceinformation',
            name='province',
            field=models.CharField(blank=True, default='مشهد', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='deviceinformation',
            name='village',
            field=models.CharField(blank=True, default='مشهد', max_length=100, null=True),
        ),
    ]
