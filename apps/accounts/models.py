from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model for the gold shop.

    Uses the user's phone number as the unique authentication
    identifier instead of Django's default username field.
    """

    # Primary authentication identifier for customer accounts.
    # The value is normalized and validated before being stored.
    phone_number = models.CharField(
        max_length=11,
        unique=True,
        db_index=True,
        validators=[
            RegexValidator(
                regex=r"^09\d{9}$",
                message="شماره موبایل باید با 09 شروع شده و 11 رقم باشد.",
            )
        ],
        verbose_name="شماره موبایل",
    )

    # Optional contact information for customer communication.
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="ایمیل",
    )

    # Basic customer identity information.
    first_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="نام",
    )

    last_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="نام خانوادگی",
    )

    # Controls whether the account is allowed to authenticate.
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    # Determines whether the user can access the Django administration site.
    is_staff = models.BooleanField(
        default=False,
        verbose_name="کارمند",
    )

    # Automatically records when the account was created.
    date_joined = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ عضویت",
    )

    # Automatically records the last modification time of the account.
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی",
    )

    # Use the custom manager for all user and superuser creation operations.
    objects = UserManager()

    # Use the phone number as the authentication identifier.
    USERNAME_FIELD = "phone_number"

    # No additional fields are required by createsuperuser.
    REQUIRED_FIELDS = []

    class Meta:
        """Database and administrative metadata for the User model."""

        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"

        # Display the newest registered users first by default.
        ordering = ["-date_joined"]

    def __str__(self):
        """Return the user's phone number as the model's display value."""

        return self.phone_number

    @property
    def full_name(self):
        """
        Return the user's complete name.

        Empty name components are automatically ignored so the result
        does not contain unnecessary leading or trailing whitespace.
        """

        return f"{self.first_name} {self.last_name}".strip()