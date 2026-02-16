from django.db import models
from django.conf import settings
from django.utils import timezone

class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Artist(models.Model):
    name = models.CharField(max_length=200)
    biography = models.TextField()
    birth_date = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='artists/', null=True, blank=True)
    genres = models.ManyToManyField(Genre, related_name='artists')

    def __str__(self):
        return self.name

class Artwork(models.Model):
    STATUS_CHOICES = [
        ('AVAILABLE', 'Disponible'),
        ('RESERVED', 'Reservada'),
        ('SOLD', 'Vendida'),
    ]

    title = models.CharField(max_length=200)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='artworks')
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, related_name='artworks')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    creation_date = models.DateField()
    photo = models.ImageField(upload_to='artworks/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    
    # Specific attributes stored as JSON
    # e.g., {"material": "bronze", "weight": "10kg", "dimensions": "10x10x10"}
    attributes = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.title

class Membership(models.Model):
    buyer_profile = models.ForeignKey('users.BuyerProfile', on_delete=models.CASCADE, related_name='memberships')
    start_date = models.DateField(auto_now_add=True)
    amount = models.DecimalField(max_digits=6, decimal_places=2, default=10.00)
    
    def __str__(self):
        return f"Membership for {self.buyer_profile.user.username}"

class Sale(models.Model):
    artwork = models.OneToOneField(Artwork, on_delete=models.CASCADE, related_name='sale')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='purchases')
    date = models.DateTimeField(default=timezone.now)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    iva = models.DecimalField(max_digits=12, decimal_places=2) # Calculated
    commission = models.DecimalField(max_digits=12, decimal_places=2) # 5-10% of price
    total = models.DecimalField(max_digits=12, decimal_places=2)
    
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='sales_processed')

    def save(self, *args, **kwargs):
        # Basic calculation logic could go here or in view
        if not self.iva:
            self.iva = self.subtotal * 0.16 # Assuming 16% IVA or similar, adapt as needed
        if not self.total:
            self.total = float(self.subtotal) + float(self.iva)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sale of {self.artwork.title}"
