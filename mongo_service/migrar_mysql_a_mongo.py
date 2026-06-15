import mysql.connector
import os
from dotenv import load_dotenv
from mongo_service.db_mongo import obras_col  # colección "obras" en MongoDB
import datetime
from decimal import Decimal

def convertir_decimals_a_floats(d):
    """Convierte recursivamente todos los valores Decimal a float en un diccionario."""
    for k, v in d.items():
        if isinstance(v, Decimal):
            d[k] = float(v)
        elif isinstance(v, dict):
            convertir_decimals_a_floats(v)   # por si hay subdocumentos
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, dict):
                    convertir_decimals_a_floats(item)
    return d

load_dotenv()

# Conexión a MySQL
mysql_conn = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    port=os.getenv("MYSQL_PORT"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DB"),
    ssl_ca=os.getenv("MYSQL_CA_FILE"),  # certificado para SSL
    ssl_disabled=False
)
cursor = mysql_conn.cursor(dictionary=True)

# 1. Cargar todos los artistas en un diccionario id -> artista
cursor.execute("SELECT id, name, nationality, biography FROM museum_artist")
artistas = {a["id"]: a for a in cursor.fetchall()}

# 2. Obtener todas las obras base con sus atributos específicos según el género
query = """
SELECT
    a.id, a.title, a.artist_id, a.genre_id, a.price, a.creation_date,
    a.photo, a.status,
    g.name AS genre_name,
    p.technique, p.support, p.height AS paint_height, p.width AS paint_width,
    s.material AS sculpt_material, s.weight, s.height AS sculpt_height,
    s.width AS sculpt_width, s.depth,
    ph.photo_type, ph.camera, ph.technique AS photo_technique,
    ph.height AS photo_height, ph.width AS photo_width,
    c.material AS cer_material, c.technique AS cer_technique,
    c.glaze_type, c.height AS cer_height, c.width AS cer_width,
    go.material AS gold_material, go.object_type, go.weight AS gold_weight,
    go.gemstones
FROM museum_artwork a
JOIN museum_genre g ON a.genre_id = g.id
LEFT JOIN museum_painting p ON a.id = p.artwork_ptr_id
LEFT JOIN museum_sculpture s ON a.id = s.artwork_ptr_id
LEFT JOIN museum_photography ph ON a.id = ph.artwork_ptr_id
LEFT JOIN museum_ceramic c ON a.id = c.artwork_ptr_id
LEFT JOIN museum_goldsmithing go ON a.id = go.artwork_ptr_id
"""
cursor.execute(query)
obras_mysql = cursor.fetchall()

# 3. Migrar cada obra a MongoDB
for obra in obras_mysql:
    obra = convertir_decimals_a_floats(obra)
    artista = artistas.get(obra["artist_id"], {})
    doc = {
        "title": obra["title"],
        "artist": {
            "_id": artista.get("id"),
            "name": artista.get("name"),
            "nationality": artista.get("nationality"),
            "biography": artista.get("biography")
        },
        "genre": obra["genre_name"],
        "price": float(obra["price"]),
        "creation_date": obra["creation_date"].isoformat() if isinstance(obra["creation_date"], datetime.date) else obra["creation_date"],
        "photo": obra.get("photo"),
        "status": obra["status"],
        "detalles_especificos": {}
    }

    # Polimorfismo: según el género, guardamos distintos campos
    genre = obra["genre_name"].lower()
    if genre == "pintura":
        doc["detalles_especificos"] = {
            "technique": obra.get("technique"),
            "support": obra.get("support"),
            "height": obra.get("paint_height"),
            "width": obra.get("paint_width")
        }
    elif genre == "escultura":
        doc["detalles_especificos"] = {
            "material": obra.get("sculpt_material"),
            "weight": obra.get("weight"),
            "height": obra.get("sculpt_height"),
            "width": obra.get("sculpt_width"),
            "depth": obra.get("depth")
        }
    elif genre == "fotografía":
        doc["detalles_especificos"] = {
            "photo_type": obra.get("photo_type"),
            "camera": obra.get("camera"),
            "technique": obra.get("photo_technique"),
            "height": obra.get("photo_height"),
            "width": obra.get("photo_width")
        }
    elif genre == "cerámica":
        doc["detalles_especificos"] = {
            "material": obra.get("cer_material"),
            "technique": obra.get("cer_technique"),
            "glaze_type": obra.get("glaze_type"),
            "height": obra.get("cer_height"),
            "width": obra.get("cer_width")
        }
    elif genre == "orfebrería":
        doc["detalles_especificos"] = {
            "material": obra.get("gold_material"),
            "object_type": obra.get("object_type"),
            "weight": obra.get("gold_weight"),
            "gemstones": obra.get("gemstones")
        }
    # Si tienes más géneros, añade otro elif

    # Insertar en MongoDB
    obras_col.insert_one(doc)

print("Migración completada. Documentos insertados:", obras_col.count_documents({}))

cursor.close()
mysql_conn.close()