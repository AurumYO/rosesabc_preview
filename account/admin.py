from django.contrib import admin
from .models import Profile, Terms


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "date_of_birth", "region", "photo"]


@admin.register(Terms)
class TermsAdmin(admin.ModelAdmin):
    list_display = [
        "date_created",
        "user_id",
        "is_active",
        "date_user_agreed_on",
        "date_updated",
    ]
    fields = (
        "user_id",
        "is_active",
        "date_user_agreed_on",
        "date_updated",
    )

