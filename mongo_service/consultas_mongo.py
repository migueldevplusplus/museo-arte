from mongo_service.db_mongo import obras_col  # colección 'obras' de MongoDB

# ------------------------------------------------------------
# Consulta 1: Filtrar por precio, género y disponibilidad
# ------------------------------------------------------------
print("=== Obras de Pintura disponibles con precio entre 1000 y 5000000 ===")
resultado = obras_col.aggregate([
    {
        "$match": {
            "genre": "Pintura",               # ajusta mayúsculas si tu género se guarda así
            "status": "AVAILABLE",
            "price": { "$gte": 1000, "$lte": 5000000 }
        }
    },
    {
        "$project": {
            "title": 1,
            "artist.name": 1,
            "price": 1,
            "status": 1,
            "_id": 0
        }
    }
])
for doc in resultado:
    print(doc)

# ------------------------------------------------------------
# Consulta 2: Filtrar por disponibilidad y género (escultura)
# ------------------------------------------------------------
print("\n=== Esculturas disponibles con peso > 50 kg ===")
resultado = obras_col.aggregate([
    {
        "$match": {
            "genre": "Escultura",
            "status": "AVAILABLE",
            "detalles_especificos.weight": { "$gt": 50 }
        }
    },
    {
        "$project": {
            "title": 1,
            "detalles_especificos.material": 1,
            "detalles_especificos.weight": 1,
            "_id": 0
        }
    }
])
for doc in resultado:
    print(doc)

# ------------------------------------------------------------
# Consulta 3: Filtrar por disponibilidad solamente
# ------------------------------------------------------------
print("\n=== Todas las obras disponibles (solo nombre y precio) ===")
resultado = obras_col.aggregate([
    { "$match": { "status": "AVAILABLE" } },
    { "$project": { "title": 1, "price": 1, "_id": 0 } }
])
for doc in resultado:
    print(doc)

# ------------------------------------------------------------
# Consulta 4: Agrupación por género (cantidad y precio promedio)
# ------------------------------------------------------------
print("\n=== Estadísticas por género ===")
resultado = obras_col.aggregate([
    {
        "$group": {
            "_id": "$genre",
            "total_obras": { "$sum": 1 },
            "precio_promedio": { "$avg": "$price" }
        }
    },
    { "$sort": { "total_obras": -1 } }
])
for doc in resultado:
    print(doc)

# ------------------------------------------------------------
# Consulta 5: Obras de un artista en particular (ejemplo con Picasso)
# ------------------------------------------------------------
print("\n=== Obras de Pablo Picasso ===")
resultado = obras_col.aggregate([
    { "$match": { "artist.name": "Pablo Picasso" } },
    { "$project": { "title": 1, "genre": 1, "price": 1, "_id": 0 } }
])
for doc in resultado:
    print(doc)