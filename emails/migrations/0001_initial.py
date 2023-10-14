# Generated by Django 4.2.3 on 2023-08-14 07:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=50, unique=True)),
                ('subject', models.CharField(max_length=50)),
                ('message', models.TextField()),
                ('attachments', models.FileField(blank=True, null=True, upload_to='email_attachments/')),
                ('status', models.CharField(choices=[('drf', 'Draft'), ('pub', 'Published')], default='drf', max_length=3)),
                ('is_active', models.BooleanField(default=True)),
                ('datetime_crated', models.DateTimeField(auto_now_add=True)),
                ('datetime_published', models.DateTimeField(auto_now_add=True, null=True)),
                ('recipients', models.ManyToManyField(related_name='received_emails', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_emails', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
