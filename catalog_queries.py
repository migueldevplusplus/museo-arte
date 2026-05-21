"""
catalog_queries.py
------------------
Sprint 1 - El Catálogo Dinámico (MongoDB)

Script de consultas usando el Aggregation Framework de MongoDB.
Cubre los tres filtros requeridos por el entregable:
  1. Filtrar por PRECIO (rango min/max)
  2. Filtrar por GÉNERO (tipo de obra)
  3. Filtrar por DISPONIBILIDAD (status)

Uso:
    python catalog_queries.py --uri "mongodb+srv://..." [opciones]

Ejemplos:
    # Ver todas las obras disponibles de Pintura con precio entre 1000 y 500000
    python catalog_queries.py --genero "Pintura" --min-precio 1000 --max-precio 500000 --status AVAILABLE

    # Ver todas las obras sin filtros (muestra todas)
    python catalog_queries.py

    # Mostrar solo obras vendidas
    python catalog_queries.py --status SOLD

    # Mostrar estadísticas del catálogo
    python catalog_queries.py --estadisticas
"""

import argparse
import sys
import pymongo
from bson.decimal128 import Decimal128


def conectar_mongodb(uri: str):
    """Establece la conexión con MongoDB y retorna la base de datos."""
    try:
        client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.server_info()  # Dispara excepción si no hay conexión
        print(f"Conexión exitosa a MongoDB.\n")
        return client["museo_arte_db"]
    except pymongo.errors.ServerSelectionTimeoutError:
        print("ERROR: No se pudo conectar a MongoDB.")
        print("Verifica que tu URI sea correcta y que el servidor esté activo.")
        sys.exit(1)


# ---------------------------------------------------------------------------
# CONSULTA 1: Filtrar por rango de precio
# ---------------------------------------------------------------------------
def query_por_precio(db, min_precio: float = None, max_precio: float = None):
    """
    Filtra obras por rango de precio usando el Aggregation Framework.
    Etapas: $match → $sort → $project
    """
    precio_filter = {}
    if min_precio is not None:
        precio_filter["$gte"] = Decimal128(str(min_precio))
    if max_precio is not None:
        precio_filter["$lte"] = Decimal128(str(max_precio))

    pipeline = [
        # Etapa 1: Filtrar por precio
        {"$match": {"price": precio_filter}},
        # Etapa 2: Ordenar de menor a mayor precio
        {"$sort": {"price": 1}},
        # Etapa 3: Proyectar solo los campos relevantes para el catálogo
        {"$project": {
            "_id": 0,
            "title": 1,
            "genre": 1,
            "status": 1,
            "artist_name": "$artist.name",
            "price": 1,
            "type": 1,
        }}
    ]
    return list(db["artworks"].aggregate(pipeline))


# ---------------------------------------------------------------------------
# CONSULTA 2: Filtrar por género
# ---------------------------------------------------------------------------
def query_por_genero(db, genero: str):
    """
    Filtra obras por género (ej. "Pintura", "Escultura", "Fotografía").
    Etapas: $match → $lookup (para traer artista completo) → $sort → $project
    """
    pipeline = [
        # Etapa 1: Filtrar exactamente por el nombre del género (embebido en el documento)
        {"$match": {"genre": genero}},
        # Etapa 2: Hacer un $lookup para traer los datos completos del artista (referencia)
        {"$lookup": {
            "from": "artists",
            "localField": "artist._id",
            "foreignField": "_id",
            "as": "artist_full"
        }},
        # Etapa 3: Aplanar el array resultante del $lookup
        {"$unwind": {"path": "$artist_full", "preserveNullAndEmptyArrays": True}},
        # Etapa 4: Ordenar alfabéticamente por título
        {"$sort": {"title": 1}},
        # Etapa 5: Proyectar incluyendo la biografía del artista (obtenida por $lookup)
        {"$project": {
            "_id": 0,
            "title": 1,
            "genre": 1,
            "status": 1,
            "price": 1,
            "type": 1,
            "artist_name": "$artist.name",
            "artist_nationality": "$artist_full.nationality",
            "specific_attributes": 1,
        }}
    ]
    return list(db["artworks"].aggregate(pipeline))


# ---------------------------------------------------------------------------
# CONSULTA 3: Filtrar por disponibilidad (status)
# ---------------------------------------------------------------------------
def query_por_disponibilidad(db, status: str = "AVAILABLE"):
    """
    Filtra obras según su estado: AVAILABLE, RESERVED, SOLD.
    Etapas: $match → $group (agrupar por género) → $sort
    """
    pipeline = [
        # Etapa 1: Filtrar por status
        {"$match": {"status": status}},
        # Etapa 2: Agrupar por género para ver cuántas hay de cada tipo disponible
        {"$group": {
            "_id": "$genre",
            "total": {"$sum": 1},
            "obras": {"$push": "$title"},
            "precio_promedio": {"$avg": "$price"}
        }},
        # Etapa 3: Ordenar por cantidad descendente
        {"$sort": {"total": -1}},
        # Etapa 4: Renombrar campo agrupador
        {"$project": {
            "_id": 0,
            "genero": "$_id",
            "total": 1,
            "obras": 1,
        }}
    ]
    return list(db["artworks"].aggregate(pipeline))


# ---------------------------------------------------------------------------
# CONSULTA 4 (BONUS): Estadísticas generales del catálogo
# ---------------------------------------------------------------------------
def query_estadisticas(db):
    """
    Pipeline de estadísticas generales: precio promedio, min, max por género.
    Muestra el poder del Aggregation Framework para análisis.
    """
    pipeline = [
        # Etapa 1: Agrupar por género calculando estadísticas de precio
        {"$group": {
            "_id": "$genre",
            "total_obras": {"$sum": 1},
            "disponibles": {"$sum": {"$cond": [{"$eq": ["$status", "AVAILABLE"]}, 1, 0]}},
            "vendidas": {"$sum": {"$cond": [{"$eq": ["$status", "SOLD"]}, 1, 0]}},
            "reservadas": {"$sum": {"$cond": [{"$eq": ["$status", "RESERVED"]}, 1, 0]}},
        }},
        # Etapa 2: Ordenar por total de obras
        {"$sort": {"total_obras": -1}},
        # Etapa 3: Renombrar el campo _id
        {"$project": {
            "_id": 0,
            "genero": "$_id",
            "total_obras": 1,
            "disponibles": 1,
            "vendidas": 1,
            "reservadas": 1,
        }}
    ]
    return list(db["artworks"].aggregate(pipeline))


# ---------------------------------------------------------------------------
# Utilidad de impresión de resultados
# ---------------------------------------------------------------------------
def imprimir_resultados(resultados, titulo: str):
    print(f"\n{'='*60}")
    print(f"  {titulo}")
    print(f"{'='*60}")
    if not resultados:
        print("  No se encontraron resultados.")
    else:
        for i, doc in enumerate(resultados, 1):
            print(f"\n  [{i}]")
            for k, v in doc.items():
                # Formatear Decimal128 a float para mejor legibilidad
                if isinstance(v, Decimal128):
                    v = float(str(v))
                if isinstance(v, list):
                    v = ", ".join(v[:5]) + ("..." if len(v) > 5 else "")
                print(f"    {k}: {v}")
    print(f"\n  Total: {len(resultados)} resultado(s)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Consultas del Catálogo de Arte usando MongoDB Aggregation Framework"
    )
    parser.add_argument(
        "--uri",
        default="mongodb://localhost:27017/",
        help="URI de conexión a MongoDB (default: mongodb://localhost:27017/)"
    )
    parser.add_argument("--min-precio", type=float, help="Precio mínimo para filtrar obras")
    parser.add_argument("--max-precio", type=float, help="Precio máximo para filtrar obras")
    parser.add_argument("--genero", type=str, help="Género de obra (ej: Pintura, Escultura, Fotografía)")
    parser.add_argument(
        "--status",
        choices=["AVAILABLE", "RESERVED", "SOLD"],
        default=None,
        help="Estado de la obra para filtrar disponibilidad"
    )
    parser.add_argument("--estadisticas", action="store_true", help="Mostrar estadísticas del catálogo")

    args = parser.parse_args()

    # Conectar a MongoDB
    db = conectar_mongodb(args.uri)

    # Ejecutar consultas según los argumentos proporcionados
    ejecuto_algo = False

    if args.min_precio is not None or args.max_precio is not None:
        ejecuto_algo = True
        resultados = query_por_precio(db, args.min_precio, args.max_precio)
        rango = f"${args.min_precio or 0} - ${args.max_precio or '∞'}"
        imprimir_resultados(resultados, f"Filtro por Precio: {rango}")

    if args.genero:
        ejecuto_algo = True
        resultados = query_por_genero(db, args.genero)
        imprimir_resultados(resultados, f"Filtro por Género: {args.genero}")

    if args.status:
        ejecuto_algo = True
        resultados = query_por_disponibilidad(db, args.status)
        imprimir_resultados(resultados, f"Filtro por Disponibilidad: {args.status}")

    if args.estadisticas:
        ejecuto_algo = True
        resultados = query_estadisticas(db)
        imprimir_resultados(resultados, "Estadísticas Generales del Catálogo por Género")

    # Si no se pasaron filtros, ejecutar todas las consultas con ejemplos predefinidos
    if not ejecuto_algo:
        print("No se especificaron filtros. Ejecutando consultas de ejemplo...\n")

        r1 = query_por_precio(db, min_precio=5000, max_precio=500000)
        imprimir_resultados(r1, "Ejemplo 1 - Obras entre $5,000 y $500,000")

        r2 = query_por_genero(db, "Pintura")
        imprimir_resultados(r2, "Ejemplo 2 - Obras de Género: Pintura")

        r3 = query_por_disponibilidad(db, "AVAILABLE")
        imprimir_resultados(r3, "Ejemplo 3 - Disponibilidad: AVAILABLE (agrupado por género)")

        r4 = query_estadisticas(db)
        imprimir_resultados(r4, "Ejemplo 4 - Estadísticas Generales del Catálogo")


if __name__ == "__main__":
    main()
