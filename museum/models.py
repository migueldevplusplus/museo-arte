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

    def get_specific_instance(self):
        """Return the child-model instance (Painting, Sculpture, etc.) if it exists."""
        for attr in ('painting', 'sculpture', 'photography', 'ceramic', 'goldsmithing'):
            try:
                return getattr(self, attr)
            except self.__class__.DoesNotExist:
                continue
            except Exception:
                continue
        return self

    def get_detail_fields(self):
        """Base implementation returns an empty list. Child models override this."""
        return []

    def __str__(self):
        return self.title


# ---------------------------------------------------------------------------
# Specialized models (multi-table inheritance)
# ---------------------------------------------------------------------------

class Painting(Artwork):
    TECHNIQUE_CHOICES = [
        ('oil', 'Óleo'),
        ('acrylic', 'Acrílico'),
        ('watercolor', 'Acuarela'),
    ]
    SUPPORT_CHOICES = [
        ('canvas', 'Lienzo'),
        ('wood', 'Madera'),
        ('paper', 'Papel'),
    ]

    technique = models.CharField(max_length=50, choices=TECHNIQUE_CHOICES)
    support = models.CharField(max_length=50, choices=SUPPORT_CHOICES)
    height = models.DecimalField(max_digits=8, decimal_places=2, help_text='Altura en cm')
    width = models.DecimalField(max_digits=8, decimal_places=2, help_text='Ancho en cm')

    class Meta:
        verbose_name = 'Pintura'
        verbose_name_plural = 'Pinturas'

    def get_detail_fields(self):
        return [
            ('Técnica', self.get_technique_display()),
            ('Soporte', self.get_support_display()),
            ('Altura', f'{self.height} cm'),
            ('Ancho', f'{self.width} cm'),
        ]


class Sculpture(Artwork):
    material = models.CharField(max_length=100)
    weight = models.DecimalField(max_digits=8, decimal_places=2, help_text='Peso en kg')
    height = models.DecimalField(max_digits=8, decimal_places=2, help_text='Altura en cm')
    width = models.DecimalField(max_digits=8, decimal_places=2, help_text='Ancho en cm')
    depth = models.DecimalField(max_digits=8, decimal_places=2, help_text='Profundidad en cm')

    class Meta:
        verbose_name = 'Escultura'
        verbose_name_plural = 'Esculturas'

    def get_detail_fields(self):
        return [
            ('Material', self.material),
            ('Peso', f'{self.weight} kg'),
            ('Altura', f'{self.height} cm'),
            ('Ancho', f'{self.width} cm'),
            ('Profundidad', f'{self.depth} cm'),
        ]


class Photography(Artwork):
    TYPE_CHOICES = [
        ('digital', 'Digital'),
        ('analog', 'Analógica'),
    ]
    TECHNIQUE_CHOICES = [
        ('bw', 'Blanco y negro'),
        ('color', 'Color'),
    ]

    photo_type = models.CharField(max_length=50, choices=TYPE_CHOICES, verbose_name='Tipo')
    camera = models.CharField(max_length=200)
    technique = models.CharField(max_length=50, choices=TECHNIQUE_CHOICES, verbose_name='Técnica')
    height = models.DecimalField(max_digits=8, decimal_places=2, help_text='Altura en cm')
    width = models.DecimalField(max_digits=8, decimal_places=2, help_text='Ancho en cm')

    class Meta:
        verbose_name = 'Fotografía'
        verbose_name_plural = 'Fotografías'

    def get_detail_fields(self):
        return [
            ('Tipo', self.get_photo_type_display()),
            ('Cámara', self.camera),
            ('Técnica', self.get_technique_display()),
            ('Altura', f'{self.height} cm'),
            ('Ancho', f'{self.width} cm'),
        ]


class Ceramic(Artwork):
    material = models.CharField(max_length=100)
    technique = models.CharField(max_length=100)
    glaze_type = models.CharField(max_length=100, verbose_name='Tipo de esmalte')
    height = models.DecimalField(max_digits=8, decimal_places=2, help_text='Altura en cm')
    width = models.DecimalField(max_digits=8, decimal_places=2, help_text='Ancho en cm')

    class Meta:
        verbose_name = 'Cerámica'
        verbose_name_plural = 'Cerámicas'

    def get_detail_fields(self):
        return [
            ('Material', self.material),
            ('Técnica', self.technique),
            ('Tipo de esmalte', self.glaze_type),
            ('Altura', f'{self.height} cm'),
            ('Ancho', f'{self.width} cm'),
        ]


class Goldsmithing(Artwork):
    MATERIAL_CHOICES = [
        ('gold', 'Oro'),
        ('silver', 'Plata'),
        ('bronze', 'Bronce'),
        ('copper', 'Cobre'),
    ]
    OBJECT_TYPE_CHOICES = [
        ('ring', 'Anillo'),
        ('necklace', 'Collar'),
        ('bracelet', 'Pulsera'),
    ]

    material = models.CharField(max_length=50, choices=MATERIAL_CHOICES)
    object_type = models.CharField(max_length=50, choices=OBJECT_TYPE_CHOICES, verbose_name='Tipo de objeto')
    weight = models.DecimalField(max_digits=8, decimal_places=2, help_text='Peso en gramos')
    gemstones = models.CharField(max_length=200, blank=True, verbose_name='Piedras preciosas')

    class Meta:
        verbose_name = 'Orfebrería'
        verbose_name_plural = 'Orfebrerías'

    def get_detail_fields(self):
        fields = [
            ('Material', self.get_material_display()),
            ('Tipo de objeto', self.get_object_type_display()),
            ('Peso', f'{self.weight} g'),
        ]
        if self.gemstones:
            fields.append(('Piedras preciosas', self.gemstones))
        return fields


# ---------------------------------------------------------------------------
# Membership & Sale (unchanged logic)
# ---------------------------------------------------------------------------

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
    iva = models.DecimalField(max_digits=12, decimal_places=2)
    commission = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='sales_processed')

    def save(self, *args, **kwargs):
        if not self.iva:
            self.iva = self.subtotal * 0.16
        if not self.total:
            self.total = float(self.subtotal) + float(self.iva)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sale of {self.artwork.title}"

class Reservation(models.Model):
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE, related_name='reservations')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reservations')
    date = models.DateTimeField(auto_now_add=True)
    security_code_used = models.CharField(max_length=10)
    
    class Meta:
        unique_together = ['artwork', 'user']  # Un usuario solo puede reservar una obra una vez
    
    def __str__(self):
        return f"{self.artwork.title} - {self.user.username}"
