"""
migrar_mysql_a_cassandra.py — ETL: MySQL → Cassandra
Sprint 2: Históricos, Auditoría y Reportes

Migra datos existentes de ventas, reservas y cambios de estatus desde
el core MySQL hacia las tablas de Cassandra.

Uso:
    python -m cassandra_service.migrar_mysql_a_cassandra
"""

import os
import sys
import uuid
from datetime import datetime
from decimal import Decimal

import mysql.connector
from dotenv import load_dotenv

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cassandra_service.db_cassandra import get_session, close

# Cargar variables de entorno
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)


def conectar_mysql():
    """Conecta a la base de datos MySQL del core transaccional."""
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
        print(f"✓ Conectado a MySQL en {config['host']}:{config['port']}")
        return conn
    except Exception as e:
        print(f"✗ Error conectando a MySQL: {e}")
        sys.exit(1)


def migrar_ventas(mysql_conn, cass_session):
    """Migra ventas de MySQL a las 3 tablas de facturación en Cassandra."""
    print("\n── Migrando ventas desde MySQL ──")

    cursor = mysql_conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            s.id          AS sale_id,
            s.date        AS sale_date,
            s.subtotal,
            s.iva,
            s.commission,
            s.total,
            s.payment_method,
            a.id          AS artwork_id,
            a.title       AS artwork_title,
            ar.name       AS artist_name,
            g.name        AS genre_name,
            u.username    AS buyer_username,
            p.username    AS processed_by
        FROM museum_sale s
        JOIN museum_artwork a   ON s.artwork_id = a.id
        JOIN museum_artist ar   ON a.artist_id = ar.id
        LEFT JOIN museum_genre g ON a.genre_id = g.id
        JOIN users_user u       ON s.buyer_id = u.id
        LEFT JOIN users_user p  ON s.processed_by_id = p.id
        ORDER BY s.date DESC
    """)
    ventas = cursor.fetchall()
    cursor.close()

    if not ventas:
        print("  ⚠ No se encontraron ventas en MySQL. Usa seed_cassandra.py para datos de prueba.")
        return 0

    # Preparar statements
    stmt_mes = cass_session.prepare("""
        INSERT INTO ventas_por_mes 
        (year, month, sale_date, sale_id, artwork_id, artwork_title, 
         artist_name, genre_name, buyer_username, payment_method,
         subtotal, iva, commission, total)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """)

    stmt_artista = cass_session.prepare("""
        INSERT INTO ventas_por_artista 
        (artist_name, sale_date, sale_id, artwork_id, artwork_title,
         genre_name, buyer_username, payment_method,
         subtotal, iva, commission, total)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """)

    stmt_genero = cass_session.prepare("""
        INSERT INTO ventas_por_genero 
        (genre_name, sale_date, sale_id, artwork_id, artwork_title,
         artist_name, buyer_username, payment_method,
         subtotal, iva, commission, total)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """)

    for v in ventas:
        sd = v["sale_date"]
        year = sd.year
        month = sd.month

        subtotal = Decimal(str(v["subtotal"]))
        iva = Decimal(str(v["iva"]))
        commission = Decimal(str(v["commission"]))
        total = Decimal(str(v["total"]))
        genre = v["genre_name"] or "Sin Género"

        # Tabla 1: ventas_por_mes
        cass_session.execute(stmt_mes, (
            year, month, sd, v["sale_id"], v["artwork_id"],
            v["artwork_title"], v["artist_name"], genre,
            v["buyer_username"], v["payment_method"],
            subtotal, iva, commission, total
        ))

        # Tabla 2: ventas_por_artista
        cass_session.execute(stmt_artista, (
            v["artist_name"], sd, v["sale_id"], v["artwork_id"],
            v["artwork_title"], genre, v["buyer_username"],
            v["payment_method"], subtotal, iva, commission, total
        ))

        # Tabla 3: ventas_por_genero
        cass_session.execute(stmt_genero, (
            genre, sd, v["sale_id"], v["artwork_id"],
            v["artwork_title"], v["artist_name"], v["buyer_username"],
            v["payment_method"], subtotal, iva, commission, total
        ))

        print(f"  ✓ Venta #{v['sale_id']}: {v['artwork_title']} → {v['buyer_username']}")

    print(f"  Total: {len(ventas)} ventas migradas a 3 tablas")
    return len(ventas)


def migrar_eventos_auditoria(mysql_conn, cass_session):
    """Genera eventos de auditoría a partir de datos existentes en MySQL."""
    print("\n── Generando eventos de auditoría desde MySQL ──")

    cursor = mysql_conn.cursor(dictionary=True)
    eventos = []

    # 1. Eventos de ventas
    cursor.execute("""
        SELECT s.id AS sale_id, s.date, a.id AS artwork_id, a.title AS artwork_title,
               u.username AS buyer, p.username AS processed_by,
               s.total
        FROM museum_sale s
        JOIN museum_artwork a ON s.artwork_id = a.id
        JOIN users_user u ON s.buyer_id = u.id
        LEFT JOIN users_user p ON s.processed_by_id = p.id
    """)
    for row in cursor.fetchall():
        eventos.append({
            "type": "VENTA",
            "timestamp": row["date"],
            "user": row["processed_by"] or "sistema",
            "description": f"Venta procesada: '{row['artwork_title']}' por ${row['total']:.2f}",
            "entity_type": "sale",
            "entity_id": str(row["sale_id"]),
            "old_value": None,
            "new_value": f"total={row['total']:.2f}",
        })

    # 2. Eventos de reservas activas
    cursor.execute("""
        SELECT r.id, r.date, a.id AS artwork_id, a.title AS artwork_title,
               u.username
        FROM museum_reservation r
        JOIN museum_artwork a ON r.artwork_id = a.id
        JOIN users_user u ON r.user_id = u.id
    """)
    for row in cursor.fetchall():
        eventos.append({
            "type": "RESERVA",
            "timestamp": row["date"],
            "user": row["username"],
            "description": f"Obra '{row['artwork_title']}' reservada por {row['username']}",
            "entity_type": "artwork",
            "entity_id": str(row["artwork_id"]),
            "old_value": "AVAILABLE",
            "new_value": "RESERVED",
        })

    # 3. Eventos de registro de compradores
    cursor.execute("""
        SELECT u.username, u.date_joined
        FROM users_user u
        WHERE u.is_buyer = 1
    """)
    for row in cursor.fetchall():
        eventos.append({
            "type": "REGISTRO_USUARIO",
            "timestamp": row["date_joined"],
            "user": row["username"],
            "description": f"Nuevo comprador registrado: {row['username']}",
            "entity_type": "user",
            "entity_id": row["username"],
            "old_value": None,
            "new_value": "BUYER",
        })

    # 4. Eventos de membresías
    cursor.execute("""
        SELECT m.id, m.start_date, m.amount, u.username
        FROM museum_membership m
        JOIN users_buyerprofile bp ON m.buyer_profile_id = bp.id
        JOIN users_user u ON bp.user_id = u.id
    """)
    for row in cursor.fetchall():
        ts = datetime.combine(row["start_date"], datetime.min.time())
        eventos.append({
            "type": "MEMBRESIA",
            "timestamp": ts,
            "user": row["username"],
            "description": f"Membresía activada para {row['username']} (${row['amount']:.2f})",
            "entity_type": "membership",
            "entity_id": str(row["id"]),
            "old_value": None,
            "new_value": "ACTIVA",
        })

    cursor.close()

    if not eventos:
        print("  ⚠ No se encontraron datos para generar eventos de auditoría.")
        return 0

    # Insertar eventos en Cassandra
    stmt = cass_session.prepare("""
        INSERT INTO bitacora_eventos 
        (event_year, event_month, event_type, event_timestamp, event_id,
         user_username, description, entity_type, entity_id, old_value, new_value)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """)

    for ev in eventos:
        ts = ev["timestamp"]
        cass_session.execute(stmt, (
            ts.year, ts.month, ev["type"], ts, uuid.uuid4(),
            ev["user"], ev["description"], ev["entity_type"],
            ev["entity_id"], ev["old_value"], ev["new_value"]
        ))

    from collections import Counter
    conteo = Counter(ev["type"] for ev in eventos)
    for tipo, cantidad in sorted(conteo.items()):
        print(f"  ✓ {tipo}: {cantidad} eventos")

    print(f"  Total: {len(eventos)} eventos migrados a bitacora_eventos")
    return len(eventos)


def migrar_historial_estatus(mysql_conn, cass_session):
    """Genera historial de estatus a partir de obras vendidas en MySQL."""
    print("\n── Generando historial de estatus desde MySQL ──")

    cursor = mysql_conn.cursor(dictionary=True)
    
    # Obras vendidas (tienen registro de venta)
    cursor.execute("""
        SELECT a.id AS artwork_id, a.title, a.status,
               s.date AS sale_date, u.username AS buyer,
               p.username AS processed_by
        FROM museum_artwork a
        JOIN museum_sale s ON s.artwork_id = a.id
        JOIN users_user u ON s.buyer_id = u.id
        LEFT JOIN users_user p ON s.processed_by_id = p.id
    """)
    vendidas = cursor.fetchall()

    # Obras reservadas
    cursor.execute("""
        SELECT a.id AS artwork_id, a.title,
               r.date AS reserve_date, u.username AS buyer
        FROM museum_artwork a
        JOIN museum_reservation r ON r.artwork_id = a.id
        JOIN users_user u ON r.user_id = u.id
        WHERE a.status = 'RESERVED'
    """)
    reservadas = cursor.fetchall()
    cursor.close()

    stmt = cass_session.prepare("""
        INSERT INTO historial_estatus_obra 
        (artwork_id, change_timestamp, artwork_title, old_status, new_status,
         changed_by, reason)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """)

    count = 0

    for v in vendidas:
        from datetime import timedelta
        fecha_venta = v["sale_date"]
        fecha_reserva = fecha_venta - timedelta(hours=24)

        # AVAILABLE → RESERVED
        cass_session.execute(stmt, (
            v["artwork_id"], fecha_reserva, v["title"],
            "AVAILABLE", "RESERVED", v["buyer"],
            f"Reserva realizada por {v['buyer']}"
        ))
        count += 1

        # RESERVED → SOLD
        cass_session.execute(stmt, (
            v["artwork_id"], fecha_venta, v["title"],
            "RESERVED", "SOLD", v["processed_by"] or "sistema",
            f"Venta procesada por {v['processed_by'] or 'sistema'}"
        ))
        count += 1

    for r in reservadas:
        cass_session.execute(stmt, (
            r["artwork_id"], r["reserve_date"], r["title"],
            "AVAILABLE", "RESERVED", r["buyer"],
            f"Reserva realizada por {r['buyer']}"
        ))
        count += 1

    print(f"  ✓ {count} registros insertados en historial_estatus_obra")
    return count


def main():
    print("=" * 60)
    print("Sprint 2 — Migración MySQL → Cassandra")
    print("=" * 60)

    mysql_conn = conectar_mysql()
    cass_session = get_session()

    total_ventas = migrar_ventas(mysql_conn, cass_session)
    total_eventos = migrar_eventos_auditoria(mysql_conn, cass_session)
    total_estatus = migrar_historial_estatus(mysql_conn, cass_session)

    mysql_conn.close()
    close()

    print(f"\n{'='*60}")
    print(f"✓ Migración completada exitosamente")
    print(f"  - {total_ventas} ventas → ventas_por_mes, ventas_por_artista, ventas_por_genero")
    print(f"  - {total_eventos} eventos → bitacora_eventos")
    print(f"  - {total_estatus} cambios → historial_estatus_obra")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
