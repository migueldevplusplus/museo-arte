import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from neo4j_service.db_neo4j import get_driver, close

def ejecutar_schema():
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.cypher')
    driver = get_driver()

    with open(schema_path, 'r', encoding='utf-8') as f:
        contenido = f.read()

    sentencias = [s.strip() for s in contenido.split(';') if s.strip()]

    ejecutadas = 0
    with driver.session() as session:
        for cql in sentencias:
            try:
                session.run(cql)
                nombre = cql.split()[2] if len(cql.split()) > 2 else cql[:40]
                print(f"  OK {cql.split()[0]} {nombre}")
                ejecutadas += 1
            except Exception as e:
                print(f"  FAIL Error: {e}")
                print(f"    Cypher: {cql[:100]}...")

    print(f"\n{'='*60}")
    print(f"OK  Esquema Neo4j creado ({ejecutadas} sentencias)")
    print(f"  Constraints: buyer_id, artwork_id, artist_id, genre_id")
    print(f"  Índices: username, title, name, genre_name")
    print(f"{'='*60}")
    close()

if __name__ == '__main__':
    print("=" * 60)
    print("Sprint 3 — Creación de Esquema Neo4j")
    print("=" * 60)
    ejecutar_schema()
