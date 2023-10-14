from django.db import models
from django.conf import settings
import os


class IPAddress(models.Model):
    ip_address = models.GenericIPAddressField(verbose_name="ادرس  آی پی")


class Instruction(models.Model):
    TYPE_CHOICES = (
        ("instruction", "دستورالعمل"),
        ("journal", "مقاله"),
        ("appreciation", "تشویق نامه"),
        ("text", "متن"),
        ("video", "ویدئو"),
        ("audio", "صوت"),
        ("image", "تصویر"),
    )
    STATUS_CHOICES = (
        ("drf", "Draft"),
        ("pub", "Published"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="instructions"
    )
    type = models.CharField(max_length=12, choices=TYPE_CHOICES, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    # pdf_file = models.FileField(verbose_name='Instruction PDF', upload_to='instructions/pdf_files/', null=True,
    #                             blank=True)
    # image_file = models.ImageField(verbose_name='Instruction Image', upload_to='instructions/image_files/', null=True,
    #                                blank=True)
    download_count = models.PositiveIntegerField(default=0)
    hits = models.ManyToManyField(
        IPAddress, blank=True, related_name="hits", verbose_name="بازدیدها"
    )

    for_behvarz = models.BooleanField(default=False)
    for_expert = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    tags = models.ManyToManyField("Tag", blank=True, null=True)

    status = models.CharField(
        max_length=3, choices=STATUS_CHOICES, null=True, blank=True, default="drf"
    )

    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-datetime_updated", "-datetime_created"]

    def __str__(self):
        return self.title

    def increment_download_count(self):
        self.download_count += 1
        self.save()


class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Attachment(models.Model):
    ins_attach = models.ForeignKey(
        "Instruction", on_delete=models.CASCADE, related_name="instruction_attach"
    )
    file = models.FileField(upload_to="Instruction_attach/", null=True, blank=True)
    file_name = models.CharField(max_length=255, default="فایل")
    file_size = models.PositiveIntegerField(default=0)
    download_count = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        self.file_name = os.path.basename(self.file.name)
        self.file_size = self.file.size

        if self.pk is None:  # در صورتی که رکورد جدید ایجاد می‌شود
            self.download_count = 0  # تنظیم تعداد دانلود به صفر

        super().save(*args, **kwargs)

    def increase_download_count(self):
        self.download_count += 1
        self.save(update_fields=["download_count"])

    def __str__(self):
        return self.file_name
