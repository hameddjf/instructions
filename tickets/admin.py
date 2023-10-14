from django.contrib import admin
from .models import Ticket, Comment, Label


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'priority', 'created_at')
    list_filter = ('status', 'priority')
    search_fields = ('title', 'description', 'user__username')
    readonly_fields = ('created_at',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'user', 'created_at')
    list_filter = ('ticket',)
    search_fields = ('ticket__title', 'text', 'user__username')
    readonly_fields = ('created_at',)


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


# این کد را اضافه کنید اگر مدل User خود را نیز به سایت ادمین اضافه کردید
# from django.contrib.auth.admin import UserAdmin
# from django.contrib.auth.models import User
# admin.site.unregister(User)
# admin.site.register(User, UserAdmin)