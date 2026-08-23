from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Administrative interface for the custom User model.

    The project uses phone numbers as the primary authentication
    identifier instead of Django's default username field.

    This configuration provides administrators with:
    - Efficient user search and filtering.
    - Read-only system-managed timestamps.
    - Structured account, personal, permission, and audit sections.
    - A dedicated form layout for creating new users.
    """

    # -------------------------------------------------------------------------
    # List View Configuration
    # -------------------------------------------------------------------------

    # Display the most recently registered users first.
    ordering = ("-date_joined",)

    # Fields displayed in the main users list.
    list_display = (
        "phone_number",
        "full_name",
        "is_active",
        "is_staff",
        "date_joined",
    )

    # Enable quick filtering by account status and administrative privileges.
    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
    )

    # Allow administrators to search users using their primary identity
    # information and basic contact details.
    search_fields = (
        "phone_number",
        "first_name",
        "last_name",
        "email",
    )

    # These values are managed automatically by the system and therefore
    # should not be editable through the admin interface.
    readonly_fields = (
        "date_joined",
        "updated_at",
        "last_login",
    )

    # -------------------------------------------------------------------------
    # User Detail View
    # -------------------------------------------------------------------------

    fieldsets = (
        (
            "اطلاعات حساب",
            {
                "fields": (
                    "phone_number",
                    "password",
                )
            },
        ),
        (
            "اطلاعات شخصی",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                )
            },
        ),
        (
            "دسترسی‌ها",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "اطلاعات زمانی",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                    "updated_at",
                )
            },
        ),
    )

    # -------------------------------------------------------------------------
    # User Creation Form
    # -------------------------------------------------------------------------

    # Defines the fields shown when an administrator creates a new user.
    # Password fields are handled by Django's UserAdmin and are securely
    # hashed before being stored in the database.
    add_fieldsets = (
        (
            "ایجاد کاربر",
            {
                "classes": ("wide",),
                "fields": (
                    "phone_number",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )