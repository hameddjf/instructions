# Generated by Django 4.2.3 on 2023-09-21 19:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('instructions', '0009_tag'),
    ]

    operations = [
        migrations.AddField(
            model_name='instruction',
            name='tags',
            field=models.ManyToManyField(blank=True, null=True, to='instructions.tag'),
        ),
    ]
