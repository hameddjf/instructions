from django.db import models
from django.conf import settings


class Ticket(models.Model):
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('close', 'Close'),
    )
    PRIORITY_CHOICES = (
        ('instantaneous', 'Instantaneous'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tickets'
    )
    title = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    comments = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Comment', related_name='ticket_comments')
    labels = models.ManyToManyField('Label', related_name='tickets')

    read_by_superuser = models.BooleanField(default=False)
    read_by_user = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Attachment(models.Model):
    ticket = models.ForeignKey('Ticket', on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='ticket_attachments/')

    def __str__(self):
        return str(self.file)


class Comment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.created_at}'


class Label(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name
