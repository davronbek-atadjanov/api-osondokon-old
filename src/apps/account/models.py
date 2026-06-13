import secrets
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

from django.db import models
from django.utils.timezone import now
from django.db.models import Q, UniqueConstraint

from apps.account.utils import generate_unique_email, generate_unique_username

class UserManager(BaseUserManager):
    def create_user(self, username=None, email=None, phone_number=None, password=None, **extra_fields):
        if not username:
            username = generate_unique_username()

        if not email:
            email = generate_unique_email()

        user = self.model(
            username=username,
            email=email,
            phone_number=phone_number,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
            extra_fields.setdefault("is_staff", True)
            extra_fields.setdefault("is_superuser", True)
            extra_fields.setdefault("is_active", True)
            return self.create_user(username=username, password=password, **extra_fields)
    
class User(AbstractBaseUser, PermissionsMixin):
    class UserType(models.TextChoices):
        DASHBOARD = "dashboard", "Dashboard"
        STORE = "store", "Store"
        MOBILE = "mobile", "Mobile"
        
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(null=True, blank=True, default=None)
    phone_number = models.CharField(max_length=64, null=True, blank=True)
    
    business_id = models.PositiveIntegerField(default=0) # default business id, 0 for dashboard and mobile users
    user_type = models.CharField(
        max_length=20, choices=UserType.choices, default=UserType.DASHBOARD, 
    )

    full_name = models.CharField(max_length=255)

    is_phone_verified = models.BooleanField(default=False)

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(auto_now_add=True)

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_user_set",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_user_permissions",
        blank=True
    )

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        constraints = [
            UniqueConstraint( # 0 2532
                fields=["business_id", "phone_number"],
                name="unique_phone_number_per_business",
                condition=~Q(phone_number=None)
            )
        ]

    def clean(self):
        """Ensure that at least one of email or phone number is provided."""
        super().clean()
        if not self.username:
            raise ValueError("Username must be provided")
        if not self.phone_number:
            raise ValueError("Phone number must be provided")

    def __str__(self):
        return f"{self.phone_number or self.username} - ({self.user_type} - {self.business_id})"

class Card(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    card_token = models.CharField(max_length=255, null=True, blank=True)
    is_verified = models.BooleanField(default=False) 
    is_default = models.BooleanField(default=True)


    def __str__(self):
        return f"{self.user} - Card Number: {self.card_number[:4]}...{self.card_number[-4:]}"

class OTP(models.Model):
    class OtpType(models.TextChoices):
        ACTIVATION = "activation", "Account Activation"
        PASSWORD_RESET = "password_reset", "Password Reset"

    EXPIRY_SECONDS = 300  # 5 minutes
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    type = models.CharField(max_length=20, choices=OtpType.choices, default=OtpType.ACTIVATION)
    attempts = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    last_sent = models.DateTimeField(auto_now_add=True)
        
    def __str__(self):
        return f"{self.user} - otp code - {self.code}"
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'type')

    @classmethod
    def generate_code(cls):
        return ''.join(secrets.choice('0123456789') for _ in range(6))
    
    def get_cooldown_time(self):
        cooldown_map = {
            0: 180,    # 3 minutes
            1: 600,    # 10 minutes
            2: 1200,    # 20 minutes
            3: 2400,   # 40 minutes
            4: 4800,   # 1 hour 20 minutes
            5: 14400   # 4 hours
        }
        return cooldown_map.get(self.attempts, 86400)  # Default 24 hours
         
    def is_expired(self):
        return (now() - self.created_at).total_seconds() > self.EXPIRY_SECONDS
    
    def can_send_new_code(self):
        """Check if a new code can be sent based on cooldown time."""
        time_passed = (now() - self.last_sent).total_seconds()
        cooldown = self.get_cooldown_time()
        
        if time_passed < cooldown:
            remaining = max(cooldown - time_passed, 0)
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            raise ValueError(f"Please wait {minutes}m {seconds}s before requesting new code")

        return True