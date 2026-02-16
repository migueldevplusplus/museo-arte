from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    is_buyer = models.BooleanField(default=False)
    is_employee = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class BuyerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='buyer_profile')
    credit_card_number = models.CharField(max_length=19, help_text="Format: XXXX-XXXX-XXXX-XXXX")
    # Basic storage for demo purposes, no real encryption
    security_code = models.CharField(max_length=10, blank=True, null=True)
    shipping_address = models.TextField(blank=True)
    
    def __str__(self):
        return f"Profile for {self.user.username}"
