import os
import django
from django.core.files.base import ContentFile
import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from museum.models import Artist, Genre, Artwork

def create_data():
    # Genres
    painting, _ = Genre.objects.get_or_create(name="Pintura")
    sculpture, _ = Genre.objects.get_or_create(name="Escultura")
    photography, _ = Genre.objects.get_or_create(name="Fotografía")

    # Artists
    picasso, _ = Artist.objects.get_or_create(
        name="Pablo Picasso",
        biography="Pintor español, creador del cubismo.",
        nationality="Española",
        birth_date=datetime.date(1881, 10, 25)
    )
    picasso.genres.add(painting, sculpture)

    dali, _ = Artist.objects.get_or_create(
        name="Salvador Dalí",
        biography="Pintor surrealista español.",
        nationality="Española",
        birth_date=datetime.date(1904, 5, 11)
    )
    dali.genres.add(painting)

    # Artworks
    Artwork.objects.get_or_create(
        title="Guernica",
        artist=picasso,
        genre=painting,
        price=15000000.00,
        creation_date=datetime.date(1937, 1, 1),
        status='AVAILABLE',
        attributes={"dimensions": "349 cm × 776 cm", "technique": "Óleo sobre lienzo"}
    )

    Artwork.objects.get_or_create(
        title="La persistencia de la memoria",
        artist=dali,
        genre=painting,
        price=2000000.00,
        creation_date=datetime.date(1931, 1, 1),
        status='AVAILABLE',
        attributes={"dimensions": "24 cm × 33 cm", "technique": "Óleo sobre lienzo"}
    )
    
    print("Data seeded successfully.")

if __name__ == "__main__":
    create_data()
