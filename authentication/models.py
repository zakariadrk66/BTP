from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from datetime import datetime, timedelta


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = None  # Remove username field
    is_2fa_enabled = models.BooleanField(default=False)
    email_2fa_code = models.CharField(max_length=6, null=True, blank=True)
    email_2fa_expires = models.DateTimeField(null=True, blank=True)
    
    USERNAME_FIELD = 'email'  # Use email to log in
    REQUIRED_FIELDS = []  # Required fields besides email and password
    
    objects = CustomUserManager()  # Use our custom manager
    
    def __str__(self):
        return self.email

    def generate_email_2fa_code(self):
        import random
        code = str(random.randint(100000, 999999))
        self.email_2fa_code = code
        self.email_2fa_expires = datetime.now() + timedelta(minutes=5)  # Code expires in 5 minutes
        self.save()
        return code