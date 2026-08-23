from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """
    Custom manager for the User model.

    Uses the user's phone number as the unique authentication
    identifier and centralizes user creation and phone number
    normalization logic.
    """

    def create_user(self, phone_number, password=None, **extra_fields):
        """Create and persist a regular user account."""

        # A phone number is required because it is the user's
        # primary authentication identifier.
        if not phone_number:
            raise ValueError("Phone number is required.")

        phone_number = self.normalize_phone_number(phone_number)

        user = self.model(
            phone_number=phone_number,
            **extra_fields,
        )

        # Regular users may be created without a password because
        # authentication can be handled through the phone-based flow.
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)

        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        """Create and persist a fully privileged administrator account."""

        # A superuser must always have a valid password for secure
        # administrative authentication.
        if not password:
            raise ValueError("Superuser must have a password.")

        # Ensure all required administrative privileges are enabled.
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        # Prevent accidentally creating an improperly configured
        # superuser account.
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(
            phone_number=phone_number,
            password=password,
            **extra_fields,
        )

    @staticmethod
    def normalize_phone_number(phone_number):
        """
        Normalize Iranian mobile numbers into a consistent format.

        Supported formats:
            09121234567
            +989121234567
            989121234567

        Stored format:
            09121234567
        """

        # Remove leading and trailing whitespace before processing.
        phone_number = phone_number.strip()

        # Convert international Iranian prefixes to the local format.
        if phone_number.startswith("+98"):
            phone_number = "0" + phone_number[3:]

        elif phone_number.startswith("98"):
            phone_number = "0" + phone_number[2:]

        # Validate the normalized number before it reaches the database.
        if not phone_number.startswith("09") or len(phone_number) != 11:
            raise ValueError("Invalid Iranian phone number.")

        # Ensure the value contains digits only.
        if not phone_number.isdigit():
            raise ValueError("Phone number must contain only digits.")

        return phone_number