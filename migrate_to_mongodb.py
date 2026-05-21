import os
import sys
import django
import decimal
import datetime
import argparse

# Configurar el entorno de Django para acceder al ORM
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

# Importar modelos de Django
from museum.models import Artist, Artwork, Painting, Sculpture, Photography, Ceramic, Goldsmithing
from bson import ObjectId
from bson.decimal128 import Decimal128
from bson.json_util import dumps

# Intentar importar pymongo (se instaló previamente)
try:
    import pymongo
except ImportError:
    print("Error: El paquete 'pymongo' no está instalado. Ejecuta 'pip install pymongo'.")
    sys.exit(1)


# Helper para generar ObjectIds deterministas basados en las llaves primarias (IDs) de MySQL
# Esto hace que el script sea idempotente (se puede ejecutar varias veces sin duplicar datos).
def get_artist_mongodb_id(mysql_id):
    # Genera una cadena hex de 24 caracteres prefijada con 'a' (para artistas)
    return ObjectId(f"a0000000000000000000{mysql_id:04x}")


def get_artwork_mongodb_id(mysql_id):
    # Genera una cadena hex de 24 caracteres prefijada con 'b' (para obras)
    return ObjectId(f"b0000000000000000000{mysql_id:04x}")


# Helper para formatear valores de Django a tipos compatibles con BSON
def clean_value(val):
    if isinstance(val, decimal.Decimal):
        return Decimal128(str(val))
    if isinstance(val, datetime.date):
        # Convertir date a datetime a medianoche para guardarlo como ISODate en MongoDB
        return datetime.datetime.combine(val, datetime.time.min)
    return val


def get_photo_path(photo_field):
    return photo_field.name if photo_field else None


def run_migration(dry_run=False, mongo_uri="mongodb://localhost:27017/"):
    print("--- INICIANDO PROCESO DE MIGRACIÓN ---")
    
    # 1. Obtener datos de Artistas
    artists_list = []
    print("\n[1/2] Mapeando Artistas desde MySQL...")
    db_artists = Artist.objects.all().prefetch_related('genres')
    
    for artist in db_artists:
        genres = [g.name for g in artist.genres.all()]
        artist_doc = {
            "_id": get_artist_mongodb_id(artist.id),
            "name": artist.name,
            "biography": artist.biography,
            "nationality": artist.nationality,
            "birth_date": clean_value(artist.birth_date),
            "photo": get_photo_path(artist.photo),
            "commission_percentage": clean_value(artist.commission_percentage),
            "genres": genres
        }
        artists_list.append(artist_doc)
    
    print(f"Mapeados {len(artists_list)} artistas con éxito.")

    # 2. Obtener datos de Obras de Arte (Artworks)
    artworks_list = []
    print("\n[2/2] Mapeando Obras de Arte con Atributos Polimórficos...")
    db_artworks = Artwork.objects.all().select_related('artist', 'genre')
    
    for artwork in db_artworks:
        # Obtener instancia específica (Painting, Sculpture, etc.) usando el método del modelo
        specific = artwork.get_specific_instance()
        
        specific_attrs = {}
        art_type = "Unknown"
        
        # Mapear atributos según el tipo específico usando herencia de tabla múltiple
        if isinstance(specific, Painting):
            art_type = "Painting"
            specific_attrs = {
                "technique": specific.technique,
                "support": specific.support,
                "height": clean_value(specific.height),
                "width": clean_value(specific.width),
            }
        elif isinstance(specific, Sculpture):
            art_type = "Sculpture"
            specific_attrs = {
                "material": specific.material,
                "weight": clean_value(specific.weight),
                "height": clean_value(specific.height),
                "width": clean_value(specific.width),
                "depth": clean_value(specific.depth),
            }
        elif isinstance(specific, Photography):
            art_type = "Photography"
            specific_attrs = {
                "photo_type": specific.photo_type,
                "camera": specific.camera,
                "technique": specific.technique,
                "height": clean_value(specific.height),
                "width": clean_value(specific.width),
            }
        elif isinstance(specific, Ceramic):
            art_type = "Ceramic"
            specific_attrs = {
                "material": specific.material,
                "technique": specific.technique,
                "glaze_type": specific.glaze_type,
                "height": clean_value(specific.height),
                "width": clean_value(specific.width),
            }
        elif isinstance(specific, Goldsmithing):
            art_type = "Goldsmithing"
            specific_attrs = {
                "material": specific.material,
                "object_type": specific.object_type,
                "weight": clean_value(specific.weight),
                "gemstones": specific.gemstones,
            }
            
        # Construir documento BSON aplicando denormalización de género y artista
        artwork_doc = {
            "_id": get_artwork_mongodb_id(artwork.id),
            "title": artwork.title,
            "price": clean_value(artwork.price),
            "creation_date": clean_value(artwork.creation_date),
            "photo": get_photo_path(artwork.photo),
            "status": artwork.status,
            "genre": artwork.genre.name if artwork.genre else None,
            "artist": {
                "_id": get_artist_mongodb_id(artwork.artist.id),
                "name": artwork.artist.name
            },
            "type": art_type,
            "specific_attributes": specific_attrs
        }
        artworks_list.append(artwork_doc)
        
    print(f"Mapeadas {len(artworks_list)} obras con éxito.")

    # 3. Procesar salida
    if dry_run:
        print("\n=== MODO DRY-RUN: Mostrando documentos JSON generados (no se guardarán en MongoDB) ===")
        print("\n--- Colección: artists ---")
        print(dumps(artists_list, indent=2, ensure_ascii=False))
        print("\n--- Colección: artworks ---")
        print(dumps(artworks_list, indent=2, ensure_ascii=False))
        print("\n--- FIN DRY-RUN ---")
        return

    # Intentar conexión e inserción en MongoDB
    print(f"\nConectando a MongoDB en: {mongo_uri} ...")
    try:
        # Se establece un timeout de selección de servidor corto (5 segundos) para no colgarse
        client = pymongo.MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        db = client["museo_arte_db"]
        
        # Verificar conexión
        client.server_info()
        
        # Colecciones
        artists_col = db["artists"]
        artworks_col = db["artworks"]
        
        # Insertar / Reemplazar artistas (usando replace_one para idempotencia)
        migrated_artists = 0
        for artist_doc in artists_list:
            artists_col.replace_one({"_id": artist_doc["_id"]}, artist_doc, upsert=True)
            migrated_artists += 1
            
        # Insertar / Reemplazar obras
        migrated_artworks = 0
        for artwork_doc in artworks_list:
            artworks_col.replace_one({"_id": artwork_doc["_id"]}, artwork_doc, upsert=True)
            migrated_artworks += 1
            
        print(f"\n¡ÉXITO! Se migraron/actualizaron {migrated_artists} artistas y {migrated_artworks} obras en MongoDB.")
        
    except pymongo.errors.ServerSelectionTimeoutError:
        print("\nERROR: No se pudo conectar a MongoDB. Asegúrate de tener MongoDB iniciado.")
        print("Puedes probar cómo quedan los documentos estructurados ejecutando el script con la opción '--dry-run':")
        print("  python migrate_to_mongodb.py --dry-run")
        sys.exit(1)
    except Exception as e:
        print(f"\nOcurrió un error inesperado durante la migración: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrar catálogo de arte desde MySQL a MongoDB.")
    parser.add_argument("--dry-run", action="store_true", help="Muestra el resultado de la transformación en JSON sin conectarse a MongoDB.")
    parser.add_argument("--uri", type=str, default="mongodb://localhost:27017/", help="URI de conexión a MongoDB.")
    
    args = parser.parse_args()
    run_migration(dry_run=args.dry_run, mongo_uri=args.uri)
