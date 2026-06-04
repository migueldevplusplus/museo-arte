"""
seed_cassandra.py — Datos de prueba para Cassandra
Sprint 2: Históricos, Auditoría y Reportes

Inserta datos sintéticos en todas las tablas de Cassandra para poder
demostrar las consultas gerenciales sin depender de ventas reales en MySQL.

Uso:
    python -m cassandra_service.seed_cassandra
"""

import os
import sys
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cassandra_service.db_cassandra import get_session, close


# ── Datos de prueba ────────────────────────────────────────────────────────

ARTISTAS = [
    "Pablo Picasso",
    "Salvador Dalí",
    "Frida Kahlo",
    "Diego Rivera",
    "Joan Miró",
]

GENEROS = ["Pintura", "Escultura", "Fotografía", "Cerámica", "Orfebrería"]

OBRAS = [
    {"id": 1,  "title": "Guernica",                   "artist": "Pablo Picasso",  "genre": "Pintura",     "price": 15000000.00},
    {"id": 2,  "title": "La Persistencia de la Memoria","artist": "Salvador Dalí", "genre": "Pintura",     "price": 8500000.00},
    {"id": 3,  "title": "Las Dos Fridas",              "artist": "Frida Kahlo",    "genre": "Pintura",     "price": 5200000.00},
    {"id": 4,  "title": "El Hombre Controlador",       "artist": "Diego Rivera",   "genre": "Pintura",     "price": 3800000.00},
    {"id": 5,  "title": "Cabeza de Toro",              "artist": "Pablo Picasso",  "genre": "Escultura",   "price": 2500000.00},
    {"id": 6,  "title": "Venus de los Cajones",        "artist": "Salvador Dalí",  "genre": "Escultura",   "price": 4200000.00},
    {"id": 7,  "title": "Autorretrato con Collar",     "artist": "Frida Kahlo",    "genre": "Fotografía",  "price": 1200000.00},
    {"id": 8,  "title": "Azul II",                     "artist": "Joan Miró",      "genre": "Pintura",     "price": 6700000.00},
    {"id": 9,  "title": "Jarrón Mediterráneo",         "artist": "Joan Miró",      "genre": "Cerámica",    "price": 950000.00},
    {"id": 10, "title": "Collar Surrealista",          "artist": "Salvador Dalí",  "genre": "Orfebrería",  "price": 1800000.00},
    {"id": 11, "title": "Mujer Sentada",               "artist": "Pablo Picasso",  "genre": "Pintura",     "price": 9100000.00},
    {"id": 12, "title": "Elefantes Cósmicos",          "artist": "Salvador Dalí",  "genre": "Escultura",   "price": 3700000.00},
    {"id": 13, "title": "La Columna Rota",             "artist": "Frida Kahlo",    "genre": "Pintura",     "price": 4500000.00},
    {"id": 14, "title": "Mural de la Industria",       "artist": "Diego Rivera",   "genre": "Pintura",     "price": 7200000.00},
    {"id": 15, "title": "Constelación Nocturna",       "artist": "Joan Miró",      "genre": "Pintura",     "price": 5800000.00},
]

COMPRADORES = ["maria_garcia", "carlos_lopez", "ana_martinez", "jose_rodriguez", "lucia_fernandez",
               "pedro_sanchez", "elena_torres", "miguel_ruiz", "sofia_morales", "daniel_vargas"]

METODOS_PAGO = ["CREDIT_CARD", "BANK_TRANSFER", "CASH", "OTHER"]

EMPLEADOS = ["admin", "empleado1", "empleado2"]


def generar_ventas():
    """Genera una lista de ventas distribuidas en varios meses."""
    import random
    random.seed(42)  # Reproducibilidad
    
    ventas = []
    sale_id = 1
    
    # Generar ventas en los últimos 6 meses
    base_date = datetime(2025, 6, 15)
    
    for obra in OBRAS:
        # Cada obra se vende una vez
        dias_atras = random.randint(0, 180)
        fecha_venta = base_date - timedelta(days=dias_atras)
        
        subtotal = Decimal(str(obra["price"]))
        iva = subtotal * Decimal("0.16")
        comision_pct = Decimal(str(random.choice([5.0, 6.5, 7.0, 8.0, 10.0])))
        commission = subtotal * (comision_pct / Decimal("100"))
        total = subtotal + iva
        
        venta = {
            "sale_id": sale_id,
            "sale_date": fecha_venta,
            "artwork_id": obra["id"],
            "artwork_title": obra["title"],
            "artist_name": obra["artist"],
            "genre_name": obra["genre"],
            "buyer_username": random.choice(COMPRADORES),
            "payment_method": random.choice(METODOS_PAGO),
            "subtotal": subtotal,
            "iva": iva,
            "commission": commission,
            "total": total,
            "processed_by": random.choice(EMPLEADOS),
        }
        ventas.append(venta)
        sale_id += 1
    
    return ventas


def insertar_ventas(session, ventas):
    """Inserta ventas en las 3 tablas de facturación."""
    print("\n── Insertando ventas en tablas de facturación ──")
    
    # Preparar statements
    stmt_mes = session.prepare("""
        INSERT INTO ventas_por_mes 
        (year, month, sale_date, sale_id, artwork_id, artwork_title, 
         artist_name, genre_name, buyer_username, payment_method,
         subtotal, iva, commission, total)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """)
    
    stmt_artista = session.prepare("""
        INSERT INTO ventas_por_artista 
        (artist_name, sale_date, sale_id, artwork_id, artwork_title,
         genre_name, buyer_username, payment_method,
         subtotal, iva, commission, total)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """)
    
    stmt_genero = session.prepare("""
        INSERT INTO ventas_por_genero 
        (genre_name, sale_date, sale_id, artwork_id, artwork_title,
         artist_name, buyer_username, payment_method,
         subtotal, iva, commission, total)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """)
    
    for v in ventas:
        year = v["sale_date"].year
        month = v["sale_date"].month
        
        # Tabla 1: ventas_por_mes
        session.execute(stmt_mes, (
            year, month, v["sale_date"], v["sale_id"], v["artwork_id"],
            v["artwork_title"], v["artist_name"], v["genre_name"],
            v["buyer_username"], v["payment_method"],
            v["subtotal"], v["iva"], v["commission"], v["total"]
        ))
        
        # Tabla 2: ventas_por_artista
        session.execute(stmt_artista, (
            v["artist_name"], v["sale_date"], v["sale_id"], v["artwork_id"],
            v["artwork_title"], v["genre_name"], v["buyer_username"],
            v["payment_method"], v["subtotal"], v["iva"], v["commission"], v["total"]
        ))
        
        # Tabla 3: ventas_por_genero
        session.execute(stmt_genero, (
            v["genre_name"], v["sale_date"], v["sale_id"], v["artwork_id"],
            v["artwork_title"], v["artist_name"], v["buyer_username"],
            v["payment_method"], v["subtotal"], v["iva"], v["commission"], v["total"]
        ))
        
        print(f"  ✓ Venta #{v['sale_id']}: {v['artwork_title']} → {v['buyer_username']} ({v['sale_date'].strftime('%Y-%m-%d')})")
    
    print(f"  Total: {len(ventas)} ventas insertadas en 3 tablas")


def insertar_bitacora(session, ventas):
    """Inserta eventos de auditoría basados en las ventas y eventos del museo."""
    import random
    random.seed(42)
    
    print("\n── Insertando eventos en bitácora ──")
    
    stmt = session.prepare("""
        INSERT INTO bitacora_eventos 
        (event_year, event_month, event_type, event_timestamp, event_id,
         user_username, description, entity_type, entity_id, old_value, new_value)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """)
    
    eventos = []
    
    for v in ventas:
        fecha_venta = v["sale_date"]
        
        # Evento: RESERVA (unos días antes de la venta)
        fecha_reserva = fecha_venta - timedelta(hours=random.randint(1, 48))
        eventos.append({
            "type": "RESERVA",
            "timestamp": fecha_reserva,
            "user": v["buyer_username"],
            "description": f"Obra '{v['artwork_title']}' reservada por {v['buyer_username']}",
            "entity_type": "artwork",
            "entity_id": str(v["artwork_id"]),
            "old_value": "AVAILABLE",
            "new_value": "RESERVED",
        })
        
        # Evento: VENTA
        eventos.append({
            "type": "VENTA",
            "timestamp": fecha_venta,
            "user": v["processed_by"],
            "description": f"Venta procesada: '{v['artwork_title']}' por ${v['total']:.2f}",
            "entity_type": "sale",
            "entity_id": str(v["sale_id"]),
            "old_value": None,
            "new_value": f"total={v['total']:.2f}",
        })
        
        # Evento: CAMBIO_ESTATUS (a SOLD)
        eventos.append({
            "type": "CAMBIO_ESTATUS",
            "timestamp": fecha_venta + timedelta(seconds=1),
            "user": v["processed_by"],
            "description": f"Estatus de '{v['artwork_title']}' cambió a SOLD",
            "entity_type": "artwork",
            "entity_id": str(v["artwork_id"]),
            "old_value": "RESERVED",
            "new_value": "SOLD",
        })
    
    # Eventos adicionales: registros de usuarios
    base_date = datetime(2025, 1, 10)
    for i, comprador in enumerate(COMPRADORES):
        fecha_registro = base_date + timedelta(days=i * 7)
        eventos.append({
            "type": "REGISTRO_USUARIO",
            "timestamp": fecha_registro,
            "user": comprador,
            "description": f"Nuevo comprador registrado: {comprador}",
            "entity_type": "user",
            "entity_id": comprador,
            "old_value": None,
            "new_value": "BUYER",
        })
    
    # Eventos: membresías
    for i, comprador in enumerate(COMPRADORES):
        fecha_membresia = base_date + timedelta(days=i * 7, hours=1)
        eventos.append({
            "type": "MEMBRESIA",
            "timestamp": fecha_membresia,
            "user": comprador,
            "description": f"Membresía activada para {comprador} ($10.00)",
            "entity_type": "membership",
            "entity_id": str(i + 1),
            "old_value": None,
            "new_value": "ACTIVA",
        })
    
    # Eventos: algunas cancelaciones de reserva
    cancelaciones = [
        {"artwork": "Azul II", "artwork_id": 8, "user": "pedro_sanchez", 
         "date": datetime(2025, 3, 20, 14, 30)},
        {"artwork": "Jarrón Mediterráneo", "artwork_id": 9, "user": "elena_torres",
         "date": datetime(2025, 4, 5, 9, 15)},
    ]
    for c in cancelaciones:
        eventos.append({
            "type": "CANCELACION",
            "timestamp": c["date"],
            "user": "empleado1",
            "description": f"Reserva cancelada: '{c['artwork']}' (reservada por {c['user']})",
            "entity_type": "artwork",
            "entity_id": str(c["artwork_id"]),
            "old_value": "RESERVED",
            "new_value": "AVAILABLE",
        })
    
    # Insertar todos los eventos
    for ev in eventos:
        ts = ev["timestamp"]
        session.execute(stmt, (
            ts.year, ts.month, ev["type"], ts, uuid.uuid4(),
            ev["user"], ev["description"], ev["entity_type"],
            ev["entity_id"], ev["old_value"], ev["new_value"]
        ))
    
    print(f"  ✓ {len(eventos)} eventos insertados en bitacora_eventos")
    
    # Resumen por tipo
    from collections import Counter
    conteo = Counter(ev["type"] for ev in eventos)
    for tipo, cantidad in sorted(conteo.items()):
        print(f"    - {tipo}: {cantidad}")


def insertar_historial_estatus(session, ventas):
    """Inserta historial de cambios de estatus para cada obra vendida."""
    import random
    random.seed(42)
    
    print("\n── Insertando historial de estatus de obras ──")
    
    stmt = session.prepare("""
        INSERT INTO historial_estatus_obra 
        (artwork_id, change_timestamp, artwork_title, old_status, new_status,
         changed_by, reason)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """)
    
    count = 0
    for v in ventas:
        fecha_venta = v["sale_date"]
        fecha_reserva = fecha_venta - timedelta(hours=random.randint(1, 48))
        
        # Cambio 1: AVAILABLE → RESERVED
        session.execute(stmt, (
            v["artwork_id"], fecha_reserva, v["artwork_title"],
            "AVAILABLE", "RESERVED", v["buyer_username"],
            f"Reserva realizada por {v['buyer_username']}"
        ))
        count += 1
        
        # Cambio 2: RESERVED → SOLD
        session.execute(stmt, (
            v["artwork_id"], fecha_venta, v["artwork_title"],
            "RESERVED", "SOLD", v["processed_by"],
            f"Venta procesada por {v['processed_by']}"
        ))
        count += 1
    
    print(f"  ✓ {count} registros insertados en historial_estatus_obra")


def main():
    print("=" * 60)
    print("Sprint 2 — Seed de Datos de Prueba (Cassandra)")
    print("=" * 60)
    
    session = get_session()
    
    # Generar datos
    ventas = generar_ventas()
    
    # Insertar en todas las tablas
    insertar_ventas(session, ventas)
    insertar_bitacora(session, ventas)
    insertar_historial_estatus(session, ventas)
    
    print(f"\n{'='*60}")
    print(f"✓ Seed completado exitosamente")
    print(f"  - {len(ventas)} ventas en 3 tablas de facturación")
    print(f"  - Eventos de auditoría en bitacora_eventos")
    print(f"  - Historial de estatus en historial_estatus_obra")
    print(f"{'='*60}")
    
    close()


if __name__ == '__main__':
    main()
