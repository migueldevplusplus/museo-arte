import os
import sys
import mysql.connector
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from neo4j_service.db_neo4j import get_driver, close

env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)

def conectar_mysql():
    ca_file = os.getenv('MYSQL_CA_FILE')
    ca_path = os.path.join(os.path.dirname(__file__), '..', ca_file) if ca_file else None
    config = {
        'host': os.getenv('MYSQL_HOST'),
        'port': int(os.getenv('MYSQL_PORT', '3306')),
        'user': os.getenv('MYSQL_USER'),
        'password': os.getenv('MYSQL_PASSWORD'),
        'database': os.getenv('MYSQL_DB'),
    }
    if ca_path and os.path.exists(ca_path):
        config['ssl_ca'] = ca_path
    try:
        conn = mysql.connector.connect(**config)
        print(f"OK  Conectado a MySQL en {config['host']}:{config['port']}")
        return conn
    except Exception as e:
        print(f"FAIL  Error conectando a MySQL: {e}")
        sys.exit(1)


def limpiar_grafo(driver):
    """Limpia el grafo completo antes de migrar."""
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
    print("  OK  Grafo limpiado")


def migrar_generos(mysql_conn, driver):
    """Migra géneros → nodos :Genre."""
    print("\n-- Migrando géneros --")
    cursor = mysql_conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name FROM museum_genre")
    generos = cursor.fetchall()
    cursor.close()
    if not generos:
        print("  ⚠ No se encontraron géneros.")
        return 0
    with driver.session() as session:
        for g in generos:
            session.run(
                "MERGE (g:Genre {id: $id}) SET g.name = $name",
                id=g['id'], name=g['name']
            )
    print(f"  OK  {len(generos)} géneros migrados")
    return len(generos)


def migrar_artistas(mysql_conn, driver):
    """Migra artistas → nodos :Artist + relación [:WORKS_IN] → :Genre."""
    print("\n-- Migrando artistas --")
    cursor = mysql_conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, nationality, biography FROM museum_artist")
    artistas = cursor.fetchall()
    cursor.close()
    if not artistas:
        print("  ⚠ No se encontraron artistas.")
        return 0

    with driver.session() as session:
        for a in artistas:
            session.run(
                """MERGE (a:Artist {id: $id})
                   SET a.name = $name, a.nationality = $nationality,
                       a.biography = $biography""",
                id=a['id'], name=a['name'],
                nationality=a['nationality'], biography=a['biography'] or ""
            )

        # Relaciones WORKS_IN con géneros
        cursor2 = mysql_conn.cursor(dictionary=True)
        cursor2.execute("SELECT artist_id, genre_id FROM museum_artist_genres")
        rels = cursor2.fetchall()
        cursor2.close()
        for r in rels:
            session.run(
                "MATCH (a:Artist {id: $aid}), (g:Genre {id: $gid}) "
                "MERGE (a)-[:WORKS_IN]->(g)",
                aid=r['artist_id'], gid=r['genre_id']
            )

        # Poblar genre_names en Artist para consultas rápidas
        session.run("""
            MATCH (a:Artist)-[:WORKS_IN]->(g:Genre)
            WITH a, collect(g.name) AS genres
            SET a.genre_names = genres
        """)

    print(f"  OK  {len(artistas)} artistas migrados con sus géneros")
    return len(artistas)


def migrar_obras_y_ventas(mysql_conn, driver):
    """Migra obras + ventas: nodos :Artwork, relaciones :CREATED y :BOUGHT."""
    print("\n-- Migrando obras y ventas --")

    # Obras
    cursor = mysql_conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.id, a.title, a.price, a.status, a.creation_date,
               a.artist_id, g.name AS genre_name
        FROM museum_artwork a
        LEFT JOIN museum_genre g ON a.genre_id = g.id
    """)
    obras = cursor.fetchall()
    cursor.close()
    if not obras:
        print("  ⚠ No se encontraron obras.")
        return 0, 0

    with driver.session() as session:
        for o in obras:
            session.run(
                """MERGE (aw:Artwork {id: $id})
                   SET aw.title = $title, aw.price = $price,
                       aw.status = $status, aw.creation_date = $creation_date,
                       aw.genre_name = $genre_name""",
                id=o['id'], title=o['title'], price=float(o['price']),
                status=o['status'],
                creation_date=str(o['creation_date']) if o['creation_date'] else None,
                genre_name=o['genre_name'] or "Sin género"
            )

        # Relaciones CREATED (Artista → Obra)
        for o in obras:
            if o['artist_id']:
                session.run(
                    "MATCH (a:Artist {id: $aid}), (aw:Artwork {id: $awid}) "
                    "MERGE (a)-[:CREATED]->(aw)",
                    aid=o['artist_id'], awid=o['id']
                )

    # Ventas (Buyer → BOUGHT → Artwork)
    cursor2 = mysql_conn.cursor(dictionary=True)
    cursor2.execute("""
        SELECT s.artwork_id, s.buyer_id, s.id AS sale_id, s.date, s.total
        FROM museum_sale s
    """)
    ventas = cursor2.fetchall()
    cursor2.close()

    with driver.session() as session:
        for v in ventas:
            # Crear nodo Buyer si no existe
            session.run(
                "MERGE (b:Buyer {id: $id})",
                id=v['buyer_id']
            )
            # Relación BOUGHT
            session.run(
                """MATCH (b:Buyer {id: $bid}), (aw:Artwork {id: $awid})
                   MERGE (b)-[:BOUGHT {sale_id: $sid, date: $date, total: $total}]->(aw)""",
                bid=v['buyer_id'], awid=v['artwork_id'],
                sid=v['sale_id'], date=str(v['date']) if v['date'] else None,
                total=float(v['total'])
            )

    # Sincronizar nombres de Buyer desde MySQL
    cursor3 = mysql_conn.cursor(dictionary=True)
    cursor3.execute("SELECT id, username, email FROM users_user WHERE is_buyer = 1")
    compradores = cursor3.fetchall()
    cursor3.close()
    with driver.session() as session:
        for c in compradores:
            session.run(
                "MERGE (b:Buyer {id: $id}) SET b.username = $username, b.email = $email",
                id=c['id'], username=c['username'], email=c['email']
            )

    print(f"  OK  {len(obras)} obras migradas")
    print(f"  OK  {len(ventas)} ventas migradas con relaciones BOUGHT")
    return len(obras), len(ventas)


def main():
    print("=" * 60)
    print("Sprint 3 — Migración MySQL → Neo4j")
    print("=" * 60)

    mysql_conn = conectar_mysql()
    driver = get_driver()
    limpiar_grafo(driver)

    total_generos = migrar_generos(mysql_conn, driver)
    total_artistas = migrar_artistas(mysql_conn, driver)
    total_obras, total_ventas = migrar_obras_y_ventas(mysql_conn, driver)

    mysql_conn.close()
    close()

    print(f"\n{'='*60}")
    print(f"OK  Migración completada exitosamente")
    print(f"  - {total_generos} géneros")
    print(f"  - {total_artistas} artistas")
    print(f"  - {total_obras} obras")
    print(f"  - {total_ventas} ventas (relaciones BOUGHT)")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
