from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from jalali_date.admin import ModelAdminJalaliMixin


from .models import CustomUser, Province, City, HealthCenter, Village


@admin.register(CustomUser)
class CustomUserAdmin(ModelAdminJalaliMixin, UserAdmin):
    list_display = [
        "username",
        "user_type",
        "birthday",
        "gender",
        "cell_phone",
        "province",
        "city",
        "health_center",
        "village",
    ]
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        (
            None,
            {
                "fields": (
                    "user_type",
                    "birthday",
                    "gender",
                    "cell_phone",
                    "security_q",
                    "security_key",
                    "province",
                    "city",
                    "health_center",
                    "village",
                )
            },
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            None,
            {
                "fields": (
                    "user_type",
                    "birthday",
                    "gender",
                    "first_name",
                    "last_name",
                    "cell_phone",
                    "province",
                    "city",
                    "health_center",
                    "village",
                    "groups",
                )
            },
        ),
    )


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    pass


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    pass


@admin.register(HealthCenter)
class HealthCenterAdmin(admin.ModelAdmin):
    pass


@admin.register(Village)
class VillageAdmin(admin.ModelAdmin):
    pass
