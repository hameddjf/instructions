from django.contrib import admin

from .models import Instruction, IPAddress, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "id")


admin.site.register(IPAddress)


@admin.register(Instruction)
class InstructionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "title",
        "for_behvarz",
        "for_expert",
        "is_active",
    )
    fieldsets = (
        ("اطلاعات پایه", {"fields": ("user", "title", "description", "number")}),
        # ('فایل‌ها', {
        #     'fields': ('pdf_file', 'image_file')
        # }),
        ("تنظیمات", {"fields": ("for_behvarz", "for_expert", "is_active")}),
        (
            "تاریخچه",
            {
                "fields": (
                    "download_count",
                    "hits",
                )
            },
        ),
    )
