import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from neo4j_service.db_neo4j import get_driver, close


def separador(titulo):
    print(f"\n{'='*70}")
    print(f"  {titulo}")
    print(f"{'='*70}")


def consulta_1_recomendaciones_por_genero(driver, username):
    """
    Q1: Recomendar obras del mismo género que el usuario ya compró,
    excluyendo las que ya adquirió.

    Cypher:
        MATCH (b:Buyer {username:$u})-[:BOUGHT]->(a:Artwork)
        WITH b, collect(DISTINCT a.genre_name) AS genres
        MATCH (other:Artist)-[:CREATED]->(rec:Artwork)
        WHERE rec.genre_name IN genres
          AND NOT (b)-[:BOUGHT]->(rec)
        RETURN DISTINCT rec.title AS obra, rec.price AS precio,
               other.name AS artista, rec.genre_name AS genero
    """
    separador(f"Q1: Recomendaciones para '{username}' (mismo género)")
    with driver.session() as session:
        result = session.run("""
            MATCH (b:Buyer {username: $u})-[:BOUGHT]->(a:Artwork)
            WITH b, collect(DISTINCT a.genre_name) AS genres
            MATCH (other:Artist)-[:CREATED]->(rec:Artwork)
            WHERE rec.genre_name IN genres
              AND NOT (b)-[:BOUGHT]->(rec)
            RETURN DISTINCT rec.title AS obra, rec.price AS precio,
                   other.name AS artista, rec.genre_name AS genero
            ORDER BY rec.price DESC
        """, u=username)
        rows = list(result)
        if not rows:
            print("  (No hay recomendaciones disponibles para este usuario)")
            return
        for r in rows:
            print(f"  · {r['obra']:<35} | ${r['precio']:>10,.2f} | "
                  f"{r['artista']:<20} | {r['genero']}")
        print(f"\n  Total: {len(rows)} recomendaciones")


def consulta_2_obras_mismo_artista(driver, username):
    """
    Q2: Obras del mismo artista que el usuario ya compró (no adquiridas).

    Cypher:
        MATCH (b:Buyer {username:$u})-[:BOUGHT]->(:Artwork)<-[:CREATED]-(a:Artist)
        MATCH (a)-[:CREATED]->(rec:Artwork)
        WHERE NOT (b)-[:BOUGHT]->(rec)
        RETURN DISTINCT rec.title AS obra, rec.price AS precio, a.name AS artista
    """
    separador(f"Q2: Obras del mismo artista para '{username}'")
    with driver.session() as session:
        result = session.run("""
            MATCH (b:Buyer {username: $u})-[:BOUGHT]->(:Artwork)<-[:CREATED]-(a:Artist)
            MATCH (a)-[:CREATED]->(rec:Artwork)
            WHERE NOT (b)-[:BOUGHT]->(rec)
            RETURN DISTINCT rec.title AS obra, rec.price AS precio, a.name AS artista
            ORDER BY rec.price DESC
        """, u=username)
        rows = list(result)
        if not rows:
            print("  (No hay obras del mismo artista disponibles)")
            return
        for r in rows:
            print(f"  · {r['obra']:<35} | ${r['precio']:>10,.2f} | {r['artista']}")
        print(f"\n  Total: {len(rows)} obras")


def consulta_3_obras_relacionadas(driver, artwork_id):
    """
    Q3: Obras relacionadas por género a una obra específica.

    Cypher:
        MATCH (aw:Artwork {id:$id})
        MATCH (other:Artist)-[:CREATED]->(related:Artwork {genre_name: aw.genre_name})
        WHERE related.id <> $id
        RETURN DISTINCT related.title AS obra, related.price AS precio,
               other.name AS artista, related.genre_name AS genero
    """
    separador(f"Q3: Obras relacionadas a la obra #{artwork_id}")
    with driver.session() as session:
        # Obtener título primero
        titulo = session.run(
            "MATCH (aw:Artwork {id:$id}) RETURN aw.title AS t",
            id=artwork_id
        ).single()
        titulo_str = titulo['t'] if titulo else f"ID {artwork_id}"
        print(f"  Obra base: {titulo_str}\n")

        result = session.run("""
            MATCH (aw:Artwork {id:$id})
            MATCH (other:Artist)-[:CREATED]->(related:Artwork {genre_name: aw.genre_name})
            WHERE related.id <> $id
            RETURN DISTINCT related.title AS obra, related.price AS precio,
                   other.name AS artista, related.genre_name AS genero
            ORDER BY related.price DESC
        """, id=artwork_id)
        rows = list(result)
        if not rows:
            print("  (No hay obras relacionadas)")
            return
        for r in rows:
            print(f"  · {r['obra']:<35} | ${r['precio']:>10,.2f} | "
                  f"{r['artista']:<20} | {r['genero']}")
        print(f"\n  Total: {len(rows)} obras relacionadas")


def consulta_4_artistas_similares(driver, artist_name):
    """
    Q4: Artistas similares (comparten género(s)).

    Cypher:
        MATCH (a1:Artist {name:$name})-[:WORKS_IN]->(g:Genre)
        MATCH (g)<-[:WORKS_IN]-(a2:Artist)
        WHERE a1 <> a2
        RETURN DISTINCT a2.name AS artista, collect(g.name) AS generos_compartidos
        ORDER BY a2.name
    """
    separador(f"Q4: Artistas similares a '{artist_name}'")
    with driver.session() as session:
        result = session.run("""
            MATCH (a1:Artist {name:$name})-[:WORKS_IN]->(g:Genre)
            MATCH (g)<-[:WORKS_IN]-(a2:Artist)
            WHERE a1 <> a2
            RETURN DISTINCT a2.name AS artista, collect(g.name) AS generos_compartidos
            ORDER BY a2.name
        """, name=artist_name)
        rows = list(result)
        if not rows:
            print("  (No se encontraron artistas similares)")
            return
        for r in rows:
            print(f"  · {r['artista']:<25} | Géneros: {', '.join(r['generos_compartidos'])}")
        print(f"\n  Total: {len(rows)} artistas similares")


def consulta_5_compradores_por_genero(driver, genre_name):
    """
    Q5: Compradores que han adquirido obras de un género específico.

    Cypher:
        MATCH (b:Buyer)-[:BOUGHT]->(a:Artwork)
        WHERE a.genre_name = $genre
        RETURN b.username AS comprador, count(a) AS obras_compradas,
               collect(a.title) AS titulos
        ORDER BY obras_compradas DESC
    """
    separador(f"Q5: Compradores del género '{genre_name}'")
    with driver.session() as session:
        result = session.run("""
            MATCH (b:Buyer)-[:BOUGHT]->(a:Artwork)
            WHERE a.genre_name = $genre
            RETURN b.username AS comprador, count(a) AS obras_compradas,
                   collect(a.title) AS titulos
            ORDER BY obras_compradas DESC
        """, genre=genre_name)
        rows = list(result)
        if not rows:
            print("  (No hay compradores para este género)")
            return
        for r in rows:
            print(f"  · {r['comprador']:<20} | {r['obras_compradas']} obra(s) | "
                  f"Títulos: {', '.join(r['titulos'])}")
        print(f"\n  Total: {len(rows)} compradores")


def menu_interactivo():
    driver = get_driver()
    opciones = {
        "1": ("Recomendaciones por género", consulta_1_recomendaciones_por_genero),
        "2": ("Obras del mismo artista", consulta_2_obras_mismo_artista),
        "3": ("Obras relacionadas", consulta_3_obras_relacionadas),
        "4": ("Artistas similares", consulta_4_artistas_similares),
        "5": ("Compradores por género", consulta_5_compradores_por_genero),
    }

    print("=" * 70)
    print("  Sprint 3 — Consultas de Recomendación (Neo4j / Cypher)")
    print("  Museo de Arte Contemporáneo")
    print("=" * 70)
    print("\n  Consultas disponibles:")
    for k, (desc, _) in opciones.items():
        print(f"    [{k}] {desc}")
    print("    [0] Salir")

    while True:
        print()
        opcion = input("  Seleccione una consulta (0-5): ").strip()
        if opcion == "0":
            break
        if opcion not in opciones:
            print("  Opción inválida.")
            continue

        desc, func = opciones[opcion]
        if opcion == "1":
            u = input("  Nombre de usuario: ").strip()
            func(driver, u)
        elif opcion == "2":
            u = input("  Nombre de usuario: ").strip()
            func(driver, u)
        elif opcion == "3":
            awid = int(input("  ID de la obra: ").strip())
            func(driver, awid)
        elif opcion == "4":
            name = input("  Nombre del artista: ").strip()
            func(driver, name)
        elif opcion == "5":
            gen = input("  Nombre del género: ").strip()
            func(driver, gen)

    close()
    print(f"\n{'='*70}")
    print("  OK  Consultas finalizadas")
    print(f"{'='*70}")


if __name__ == '__main__':
    menu_interactivo()
