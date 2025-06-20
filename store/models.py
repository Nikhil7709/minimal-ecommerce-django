from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from store.abstract import AbstractAuditCreator, AbstractAuditUpdater 
from store import STATUSCHOICES

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


class Product(AbstractAuditCreator, AbstractAuditUpdater):
    """
    Represents a product available for purchase, including price, stock,
    and relationships to category and creator (user).
    """
    name = models.CharField(max_length=255)
    description = models.TextField(
        blank=True, 
        null=True
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    stock = models.PositiveIntegerField()

    # F.Ks
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_category"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "3. Products"


class Cart(AbstractAuditCreator, AbstractAuditUpdater):
    """
    Shopping cart assigned to a single user, holds cart items.
    """
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_user"
    )

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "4. Carts"


class CartItem(AbstractAuditCreator, AbstractAuditUpdater):
    """
    Represents a product added to a cart with a specified quantity.
    Each product appears once per cart.
    """

    quantity = models.PositiveIntegerField(default=1)

    # F.Ks
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_cart"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_product"
    )

    def __str__(self):
        return f"{self.cart} - {self.product}"

    class Meta:
        unique_together = ['cart', 'product']
        verbose_name = "Cart Item"
        verbose_name_plural = "5. Cart Items"


class Order(AbstractAuditCreator, AbstractAuditUpdater):
    """
    Represents an order placed by a user with total amount and status.
    """
    total_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2
    )
    status = models.CharField(
        max_length=16,
        choices=STATUSCHOICES.choices,
        default=STATUSCHOICES.PENDING
    )
    ordered_at = models.DateTimeField(auto_now_add=True)

    # F.Ks
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_user"
    )

    def __str__(self):
        return f"{self.user} - {self.status}"

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "6. Orders"


class OrderItem(AbstractAuditCreator, AbstractAuditUpdater):
    """
    Line item for an order, referencing product, quantity,
    and price at the time of order.
    """

    quantity = models.PositiveIntegerField()
    price_at_order_time = models.DecimalField(
        max_digits=10, 
        decimal_places=2
    )

    # F.Ks
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_order"
    )
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="%(app_label)s_%(class)s_product"
    )

    def __str__(self):
        return f"{self.order} - {self.product}"

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

