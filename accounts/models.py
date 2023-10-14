from django.db import models
from django.contrib.auth.models import AbstractUser
from django.shortcuts import reverse
from temps.models import Device


class Province(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

    def get_absolute_get(self):
        return reverse("province_detail", args=[str(self.id)])


class City(models.Model):
    province = models.ForeignKey(
        Province, on_delete=models.CASCADE, related_name="province_cities"
    )
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("city_delete", args={str(self.id)})


class HealthCenter(models.Model):
    city = models.ForeignKey(
        City, on_delete=models.CASCADE, related_name="city_healthCenter"
    )
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Village(models.Model):
    health_center = models.ForeignKey(
        HealthCenter, on_delete=models.CASCADE, related_name="health_village"
    )
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ("manager", "Manager"),
        ("expert", "Expert"),
        ("behvarz", "Behvarz"),
    )
    GENDER_CHOICES = (
        ("man", "Man"),
        ("women", "Women"),
        ("other", "Other"),
    )
    EDU_CHOICES = (
        ("High school", "High school"),
        ("Diploma", "Diploma"),
        ("Associate Degree", "Associate Degree"),
        ("Bachelor degree", "Bachelor degree"),
    )
    SECURITY_Q = (
        ("1", "نام اولین دبیر شما چه بود؟"),
        ("2", "نام بهترین کتابی که خوانده اید چه بود؟"),
        ("3", "نام رنگ مورد علاقه شما چیست؟"),
        ("4", "غذای مورد علاقه شما چیست؟"),
    )
    user_type = models.CharField(
        max_length=7, choices=USER_TYPE_CHOICES, blank=True, null=True
    )
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=5, choices=GENDER_CHOICES, blank=True, null=True
    )
    education = models.CharField(
        max_length=20, choices=EDU_CHOICES, null=True, blank=True
    )
    photo = models.ImageField(upload_to="accounts/users_avatar/", blank=True, null=True)

    cell_phone = models.IntegerField(blank=True, null=True)

    province = models.ForeignKey(
        Province, on_delete=models.CASCADE, null=True, blank=True
    )
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True, blank=True)
    health_center = models.ForeignKey(
        HealthCenter, on_delete=models.CASCADE, null=True, blank=True
    )
    village = models.ForeignKey(
        Village, on_delete=models.CASCADE, null=True, blank=True
    )

    security_q = models.CharField(
        max_length=20, choices=SECURITY_Q, null=True, blank=True
    )
    security_key = models.CharField(max_length=120, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_absolute_url(self):
        return reverse("profile", kwargs={"pk": self.id})
