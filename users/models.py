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
    
    SECURITY_QUESTIONS = (
        ('q1', '¿Cuál es tu color favorito?'),
        ('q2', '¿En qué ciudad naciste?'),
        ('q3', '¿Cual es el nombre de soltera de tu madre?'),
        ('q4', '¿Cuál fue el modelo de tu primer coche?'),
        ('q5', '¿Cuál es el nombre de tu escuela primaria?'),
    )

    security_question_1 = models.CharField(max_length=2, choices=SECURITY_QUESTIONS, blank=True, null=True)
    security_answer_1 = models.CharField(max_length=100, blank=True, null=True)
    security_question_2 = models.CharField(max_length=2, choices=SECURITY_QUESTIONS, blank=True, null=True)
    security_answer_2 = models.CharField(max_length=100, blank=True, null=True)
    security_question_3 = models.CharField(max_length=2, choices=SECURITY_QUESTIONS, blank=True, null=True)
    security_answer_3 = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"Profile for {self.user.username}"
