from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from store.abstract import AbstractAuditCreator, AbstractAuditUpdater 

# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is mandatory')
        email = self.normalize_email(email)
        user = self.model(
            email=email, 
            name=name, 
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        return self.create_user(email, name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=256)
    email = models.EmailField(
        max_length=256, 
        unique=True
    )
    password = models.CharField(max_length=128)
    is_admin = models.BooleanField(default=False)
    is_creator = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "1. Users"


class Category(AbstractAuditCreator, AbstractAuditUpdater):
    """
    Represents a product category with a unique slug.
    Used to classify and group products.
    """

    name = models.CharField(
        max_length=128, 
        unique=True
    )
    slug = models.SlugField(
        unique=True, 
        blank=True
    )

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "2. Categories"