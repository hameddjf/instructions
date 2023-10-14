from django.conf import settings

from django.db import models


class Email(models.Model):
    STATUS_CHOICES = (
        ("drf", "Draft"),
        ("pub", "Published"),
    )
    number = models.CharField(max_length=50, unique=True)
    subject = models.CharField(max_length=50)
    message = models.TextField()

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_emails"
    )
    recipients = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="received_emails"
    )

    attachments = models.FileField(
        upload_to="email_attachments/", blank=True, null=True
    )

    status = models.CharField(max_length=3, choices=STATUS_CHOICES, default="drf")
    is_active = models.BooleanField(default=True)

    datetime_crated = models.DateTimeField(auto_now_add=True)
    datetime_published = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.subject
