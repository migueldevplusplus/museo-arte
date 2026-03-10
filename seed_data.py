import os
import django
import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from museum.models import Artist, Genre, Painting, Sculpture


def create_data():
    # Genres (all five)
    painting_genre, _ = Genre.objects.get_or_create(name="Pintura")
    sculpture_genre, _ = Genre.objects.get_or_create(name="Escultura")
    Genre.objects.get_or_create(name="Fotografía")
    Genre.objects.get_or_create(name="Cerámica")
    Genre.objects.get_or_create(name="Orfebrería")

    # Artists
    picasso, _ = Artist.objects.get_or_create(
        name="Pablo Picasso",
        defaults={
            "biography": "Pablo Picasso (1881-1973) fue un pintor y escultor español, cofundador del Cubismo y uno de los artistas más influyentes del siglo XX, conocido por obras revolucionarias como 'Las Señoritas de Aviñón' (1907) y su mural antibélico 'Guernica' (1937); su carrera abarcó periodos como el Azul y el Rosa, y su increíble productividad (más de 50,000 obras) transformó permanentemente el arte moderno.",
            "nationality": "Española",
            "birth_date": datetime.date(1881, 10, 25),
        },
    )
    picasso.genres.add(painting_genre, sculpture_genre)

    dali, _ = Artist.objects.get_or_create(
        name="Salvador Dalí",
        defaults={
            "biography": "Pintor surrealista español.",
            "nationality": "Española",
            "birth_date": datetime.date(1904, 5, 11),
        },
    )
    dali.genres.add(painting_genre)

    # Artworks — using specialized models
    Painting.objects.get_or_create(
        title="Guernica",
        defaults={
            "artist": picasso,
            "genre": painting_genre,
            "price": 15000000.00,
            "creation_date": datetime.date(1937, 1, 1),
            "status": "AVAILABLE",
            "technique": "oil",
            "support": "canvas",
            "height": 349,
            "width": 776,
        },
    )

    Painting.objects.get_or_create(
        title="La persistencia de la memoria",
        defaults={
            "artist": dali,
            "genre": painting_genre,
            "price": 2000000.00,
            "creation_date": datetime.date(1931, 1, 1),
            "status": "AVAILABLE",
            "technique": "oil",
            "support": "canvas",
            "height": 24,
            "width": 33,
        },
    )

    print("Data seeded successfully.")


if __name__ == "__main__":
    create_data()
