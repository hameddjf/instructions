# Generated by Django 4.2.3 on 2023-08-26 20:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('instructions', '0005_attachment'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachment',
            name='file_name',
            field=models.CharField(default='فایل', max_length=255),
        ),
        migrations.AddField(
            model_name='attachment',
            name='file_size',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
