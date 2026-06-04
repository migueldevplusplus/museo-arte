"""
crear_esquema.py — Crea el keyspace y las tablas en Cassandra
Sprint 2: Históricos, Auditoría y Reportes

Ejecuta el archivo schema.cql línea por línea contra el cluster.

Uso:
    python -m cassandra_service.crear_esquema
"""

import os
import sys
import re

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cassandra_service.db_cassandra import get_session_without_keyspace


def ejecutar_schema():
    """Lee schema.cql y ejecuta cada sentencia."""
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.cql')

    with open(schema_path, 'r', encoding='utf-8') as f:
        contenido = f.read()

    # Separar sentencias por punto y coma
    sentencias = contenido.split(';')

    session, cluster = get_session_without_keyspace()

    ejecutadas = 0
    for sentencia in sentencias:
        # Limpiar comentarios de línea y espacios
        lineas = []
        for linea in sentencia.split('\n'):
            linea_limpia = linea.split('--')[0]  # Quitar comentarios
            lineas.append(linea_limpia)
        
        cql = '\n'.join(lineas).strip()
        
        if not cql:
            continue

        try:
            session.execute(cql)
            # Extraer el nombre de la operación para el log
            match = re.search(r'(CREATE\s+\w+|USE)\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+\.?\w*)', cql, re.IGNORECASE)
            if match:
                operacion = match.group(1).upper()
                nombre = match.group(2)
                print(f"  ✓ {operacion} {nombre}")
            ejecutadas += 1
        except Exception as e:
            print(f"  ✗ Error ejecutando sentencia: {e}")
            print(f"    CQL: {cql[:100]}...")

    print(f"\n{'='*60}")
    print(f"✓ Esquema creado exitosamente ({ejecutadas} sentencias ejecutadas)")
    print(f"  Keyspace: museo")
    print(f"  Tablas: ventas_por_mes, ventas_por_artista, ventas_por_genero,")
    print(f"          bitacora_eventos, historial_estatus_obra")
    print(f"{'='*60}")

    session.shutdown()
    cluster.shutdown()


if __name__ == '__main__':
    print("=" * 60)
    print("Sprint 2 — Creación de Esquema Cassandra")
    print("=" * 60)
    ejecutar_schema()
