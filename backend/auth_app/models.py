from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    CUSTOMER = 'customer'
    BUSINESS = 'business'

    USER_TYPE_CHOICES = [
        (CUSTOMER, 'Customer'),
        (BUSINESS, 'Business'),
    ]

    type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
    )

    def __str__(self):
        return self.username
