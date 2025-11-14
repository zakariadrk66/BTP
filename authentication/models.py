from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

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
    
    USERNAME_FIELD = 'email'  # Use email to log in
    REQUIRED_FIELDS = []  # Required fields besides email and password
    
    objects = CustomUserManager()  # Use our custom manager
    
    def __str__(self):
        return self.email