import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from neo4j_service.db_neo4j import get_driver, close


def limpiar_grafo(driver):
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
    print("  OK  Grafo limpiado")


def seed(driver):
    print("\n --  Insertando datos sintéticos  -- ")

    generos = [
        {"id": 1, "name": "Pintura"},
        {"id": 2, "name": "Escultura"},
        {"id": 3, "name": "Fotografía"},
        {"id": 4, "name": "Cerámica"},
        {"id": 5, "name": "Orfebrería"},
    ]
    artistas = [
        {"id": 1, "name": "Pablo Picasso", "nationality": "Española", "biography": "Pintor y escultor español, cofundador del Cubismo."},
        {"id": 2, "name": "Salvador Dalí", "nationality": "Española", "biography": "Pintor surrealista español."},
        {"id": 3, "name": "Frida Kahlo", "nationality": "Mexicana", "biography": "Pintora mexicana conocida por sus autorretratos."},
        {"id": 4, "name": "Diego Rivera", "nationality": "Mexicana", "biography": "Muralista mexicano."},
        {"id": 5, "name": "Joan Miró", "nationality": "Española", "biography": "Pintor, escultor y ceramista surrealista."},
    ]
    obras = [
        {"id": 1, "title": "Guernica", "price": 15000000, "status": "SOLD", "artist_id": 1, "genre_name": "Pintura"},
        {"id": 2, "title": "La persistencia de la memoria", "price": 8500000, "status": "AVAILABLE", "artist_id": 2, "genre_name": "Pintura"},
        {"id": 3, "title": "Las dos Fridas", "price": 12000000, "status": "RESERVED", "artist_id": 3, "genre_name": "Pintura"},
        {"id": 4, "title": "El hombre en la encrucijada", "price": 9500000, "status": "AVAILABLE", "artist_id": 4, "genre_name": "Pintura"},
        {"id": 5, "title": "Mujer y pájaro", "price": 3200000, "status": "AVAILABLE", "artist_id": 5, "genre_name": "Escultura"},
        {"id": 6, "title": "El nacimiento del mundo", "price": 5500000, "status": "SOLD", "artist_id": 1, "genre_name": "Pintura"},
    ]
    compradores = [
        {"id": 1, "username": "juanperez", "email": "juan@email.com"},
        {"id": 2, "username": "marialopez", "email": "maria@email.com"},
        {"id": 3, "username": "carlosgomez", "email": "carlos@email.com"},
    ]

    with driver.session() as session:
        # Géneros
        for g in generos:
            session.run("MERGE (g:Genre {id: $id}) SET g.name = $name", id=g['id'], name=g['name'])

        # Artistas
        for a in artistas:
            session.run(
                "MERGE (a:Artist {id: $id}) SET a.name = $name, a.nationality = $nationality, a.biography = $biography",
                id=a['id'], name=a['name'], nationality=a['nationality'], biography=a['biography']
            )

        # Relaciones Artista → WORKS_IN → Género
        relaciones = [(1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (5, 2)]
        for aid, gid in relaciones:
            session.run(
                "MATCH (a:Artist {id: $aid}), (g:Genre {id: $gid}) MERGE (a)-[:WORKS_IN]->(g)",
                aid=aid, gid=gid
            )

        # genre_names en Artist
        session.run("""
            MATCH (a:Artist)-[:WORKS_IN]->(g:Genre)
            WITH a, collect(g.name) AS genres
            SET a.genre_names = genres
        """)

        # Obras
        for o in obras:
            session.run(
                """MERGE (aw:Artwork {id: $id})
                   SET aw.title = $title, aw.price = $price, aw.status = $status,
                       aw.genre_name = $genre_name""",
                id=o['id'], title=o['title'], price=o['price'],
                status=o['status'], genre_name=o['genre_name']
            )

        # Relaciones CREATED
        for o in obras:
            session.run(
                "MATCH (a:Artist {id: $aid}), (aw:Artwork {id: $awid}) MERGE (a)-[:CREATED]->(aw)",
                aid=o['artist_id'], awid=o['id']
            )

        # Compradores
        for c in compradores:
            session.run(
                "MERGE (b:Buyer {id: $id}) SET b.username = $username, b.email = $email",
                id=c['id'], username=c['username'], email=c['email']
            )

        # Relaciones BOUGHT
        ventas = [
            (1, 1, "2026-03-15", 16500000.00),
            (1, 6, "2026-04-01", 6380000.00),
            (2, 1, "2026-05-10", 16500000.00),
            (3, 6, "2026-06-01", 6380000.00),
        ]
        for bid, awid, fecha, total in ventas:
            session.run(
                """MATCH (b:Buyer {id: $bid}), (aw:Artwork {id: $awid})
                   MERGE (b)-[:BOUGHT {sale_id: $sid, date: $date, total: $total}]->(aw)""",
                bid=bid, awid=awid, sid=hash((bid, awid)) % 10000, date=fecha, total=total
            )

    print(f"  OK  {len(generos)} géneros")
    print(f"  OK  {len(artistas)} artistas")
    print(f"  OK  {len(obras)} obras")
    print(f"  OK  {len(compradores)} compradores")
    print(f"  OK  {len(ventas)} ventas (BOUGHT)")


def main():
    print("=" * 60)
    print("Sprint 3 — Seed Neo4j (Datos Sintéticos)")
    print("=" * 60)
    driver = get_driver()
    limpiar_grafo(driver)
    seed(driver)
    close()
    print(f"\nOK  Seed completado. Ver en http://localhost:7474")
    print(f"  Usuario: neo4j | Contraseña: password")


if __name__ == '__main__':
    main()
