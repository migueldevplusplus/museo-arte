"""
consultas_cassandra.py — Consultas Gerenciales CQL
Sprint 2: Históricos, Auditoría y Reportes

Demuestra las consultas que responde cada tabla de Cassandra,
optimizadas por Query-Driven Modeling.

Uso:
    python -m cassandra_service.consultas_cassandra
"""

import os
import sys
from decimal import Decimal

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cassandra_service.db_cassandra import get_session, close


def separador(titulo):
    """Imprime un separador visual para cada consulta."""
    print(f"\n{'═'*70}")
    print(f"  {titulo}")
    print(f"{'═'*70}")


# ════════════════════════════════════════════════════════════════════════════
# CONSULTAS DE FACTURACIÓN
# ════════════════════════════════════════════════════════════════════════════

def consulta_1_facturacion_mensual(session, year, month):
    """
    Q1: Resumen de facturación de un mes específico.
    
    Tabla: ventas_por_mes
    Partition Key: (year, month)
    
    CQL equivalente:
        SELECT * FROM ventas_por_mes WHERE year = ? AND month = ?;
    """
    separador(f"Q1: Facturación del mes {month}/{year}")
    
    rows = session.execute(
        "SELECT * FROM ventas_por_mes WHERE year = %s AND month = %s",
        (year, month)
    )
    
    total_subtotal = Decimal('0')
    total_iva = Decimal('0')
    total_comision = Decimal('0')
    total_facturado = Decimal('0')
    count = 0
    
    for row in rows:
        count += 1
        total_subtotal += row.subtotal
        total_iva += row.iva
        total_comision += row.commission
        total_facturado += row.total
        print(f"  #{row.sale_id} | {row.sale_date.strftime('%Y-%m-%d')} | "
              f"{row.artwork_title[:30]:<30} | {row.artist_name:<20} | "
              f"${row.total:>12,.2f}")
    
    if count == 0:
        print("  (No hay ventas en este período)")
        return
    
    print(f"\n  {'─'*65}")
    print(f"  RESUMEN DEL MES {month}/{year}:")
    print(f"    Ventas realizadas:  {count}")
    print(f"    Subtotal:           ${total_subtotal:>12,.2f}")
    print(f"    IVA (16%):          ${total_iva:>12,.2f}")
    print(f"    Comisión museo:     ${total_comision:>12,.2f}")
    print(f"    TOTAL FACTURADO:    ${total_facturado:>12,.2f}")


def consulta_2_facturacion_periodo(session, year_start, month_start, year_end, month_end):
    """
    Q2: Resumen de facturación en un rango de meses.
    
    Nota: Cassandra no permite range queries sobre partition keys,
    por lo que iteramos mes por mes (diseño correcto para este caso).
    """
    separador(f"Q2: Facturación del período {month_start}/{year_start} al {month_end}/{year_end}")
    
    gran_total = Decimal('0')
    gran_subtotal = Decimal('0')
    gran_iva = Decimal('0')
    gran_comision = Decimal('0')
    total_ventas = 0
    
    # Iterar mes por mes
    year, month = year_start, month_start
    while (year, month) <= (year_end, month_end):
        rows = session.execute(
            "SELECT subtotal, iva, commission, total FROM ventas_por_mes WHERE year = %s AND month = %s",
            (year, month)
        )
        
        mes_total = Decimal('0')
        mes_count = 0
        
        for row in rows:
            mes_total += row.total
            gran_subtotal += row.subtotal
            gran_iva += row.iva
            gran_comision += row.commission
            gran_total += row.total
            mes_count += 1
            total_ventas += 1
        
        if mes_count > 0:
            print(f"  {month:02d}/{year}: {mes_count} ventas → ${mes_total:>12,.2f}")
        
        # Avanzar al siguiente mes
        month += 1
        if month > 12:
            month = 1
            year += 1
    
    print(f"\n  {'─'*65}")
    print(f"  RESUMEN DEL PERÍODO:")
    print(f"    Total ventas:       {total_ventas}")
    print(f"    Subtotal:           ${gran_subtotal:>12,.2f}")
    print(f"    IVA acumulado:      ${gran_iva:>12,.2f}")
    print(f"    Comisión museo:     ${gran_comision:>12,.2f}")
    print(f"    TOTAL FACTURADO:    ${gran_total:>12,.2f}")


def consulta_3_ventas_por_artista(session, artist_name):
    """
    Q3: Todas las ventas de un artista específico.
    
    Tabla: ventas_por_artista
    Partition Key: (artist_name)
    
    CQL equivalente:
        SELECT * FROM ventas_por_artista WHERE artist_name = ?;
    """
    separador(f"Q3: Ventas del artista '{artist_name}'")
    
    rows = session.execute(
        "SELECT * FROM ventas_por_artista WHERE artist_name = %s",
        (artist_name,)
    )
    
    total = Decimal('0')
    total_comision = Decimal('0')
    count = 0
    
    for row in rows:
        count += 1
        total += row.total
        total_comision += row.commission
        print(f"  #{row.sale_id} | {row.sale_date.strftime('%Y-%m-%d')} | "
              f"{row.artwork_title[:35]:<35} | {row.genre_name:<12} | "
              f"${row.total:>12,.2f}")
    
    if count == 0:
        print(f"  (No hay ventas registradas para '{artist_name}')")
        return
    
    print(f"\n  {'─'*65}")
    print(f"  Total ventas de {artist_name}: {count}")
    print(f"  Facturación total:   ${total:>12,.2f}")
    print(f"  Comisión generada:   ${total_comision:>12,.2f}")


def consulta_4_ventas_por_genero(session, genre_name):
    """
    Q4: Todas las ventas de un género artístico.
    
    Tabla: ventas_por_genero
    Partition Key: (genre_name)
    
    CQL equivalente:
        SELECT * FROM ventas_por_genero WHERE genre_name = ?;
    """
    separador(f"Q4: Ventas del género '{genre_name}'")
    
    rows = session.execute(
        "SELECT * FROM ventas_por_genero WHERE genre_name = %s",
        (genre_name,)
    )
    
    total = Decimal('0')
    count = 0
    
    for row in rows:
        count += 1
        total += row.total
        print(f"  #{row.sale_id} | {row.sale_date.strftime('%Y-%m-%d')} | "
              f"{row.artwork_title[:30]:<30} | {row.artist_name:<20} | "
              f"${row.total:>12,.2f}")
    
    if count == 0:
        print(f"  (No hay ventas registradas para el género '{genre_name}')")
        return
    
    print(f"\n  {'─'*65}")
    print(f"  Total ventas de {genre_name}: {count}")
    print(f"  Facturación total: ${total:>12,.2f}")


def consulta_5_ranking_artistas(session, artistas):
    """
    Q5: Ranking de artistas por facturación total.
    
    Itera sobre cada artista para construir el ranking.
    En producción, esto se mantendría en una tabla materializada aparte.
    """
    separador("Q5: Ranking de artistas por facturación")
    
    ranking = []
    
    for artista in artistas:
        rows = session.execute(
            "SELECT total, commission FROM ventas_por_artista WHERE artist_name = %s",
            (artista,)
        )
        total = Decimal('0')
        comision = Decimal('0')
        count = 0
        for row in rows:
            total += row.total
            comision += row.commission
            count += 1
        if count > 0:
            ranking.append((artista, count, total, comision))
    
    ranking.sort(key=lambda x: x[2], reverse=True)
    
    print(f"  {'Pos':<4} {'Artista':<25} {'Ventas':<8} {'Facturación':<15} {'Comisión Museo':<15}")
    print(f"  {'─'*67}")
    for i, (artista, count, total, comision) in enumerate(ranking, 1):
        print(f"  {i:<4} {artista:<25} {count:<8} ${total:>12,.2f}  ${comision:>12,.2f}")


def consulta_6_ranking_generos(session, generos):
    """
    Q6: Ranking de géneros por facturación total.
    """
    separador("Q6: Ranking de géneros por facturación")
    
    ranking = []
    
    for genero in generos:
        rows = session.execute(
            "SELECT total FROM ventas_por_genero WHERE genre_name = %s",
            (genero,)
        )
        total = Decimal('0')
        count = 0
        for row in rows:
            total += row.total
            count += 1
        if count > 0:
            ranking.append((genero, count, total))
    
    ranking.sort(key=lambda x: x[2], reverse=True)
    
    print(f"  {'Pos':<4} {'Género':<20} {'Ventas':<8} {'Facturación':<15}")
    print(f"  {'─'*50}")
    for i, (genero, count, total) in enumerate(ranking, 1):
        print(f"  {i:<4} {genero:<20} {count:<8} ${total:>12,.2f}")


# ════════════════════════════════════════════════════════════════════════════
# CONSULTAS DE AUDITORÍA
# ════════════════════════════════════════════════════════════════════════════

def consulta_7_bitacora_por_tipo(session, event_type, year, month):
    """
    Q7: Eventos de auditoría por tipo en un mes específico.
    
    Tabla: bitacora_eventos
    Partition Key: (event_year, event_month, event_type)
    
    CQL equivalente:
        SELECT * FROM bitacora_eventos 
        WHERE event_year = ? AND event_month = ? AND event_type = ?;
    """
    separador(f"Q7: Bitácora de eventos '{event_type}' en {month}/{year}")
    
    rows = session.execute(
        """SELECT * FROM bitacora_eventos 
           WHERE event_year = %s AND event_month = %s AND event_type = %s""",
        (year, month, event_type)
    )
    
    count = 0
    for row in rows:
        count += 1
        old_val = row.old_value or "—"
        new_val = row.new_value or "—"
        print(f"  {row.event_timestamp.strftime('%Y-%m-%d %H:%M')} | "
              f"{row.user_username:<18} | {row.description[:50]}")
        if old_val != "—" or new_val != "—":
            print(f"  {'':>19} └─ {old_val} → {new_val}")
    
    if count == 0:
        print(f"  (No hay eventos de tipo '{event_type}' en {month}/{year})")
    else:
        print(f"\n  Total: {count} eventos")


def consulta_8_todos_los_eventos_mes(session, year, month):
    """
    Q8: Todos los eventos de auditoría de un mes (todos los tipos).
    """
    separador(f"Q8: Todos los eventos de auditoría en {month}/{year}")
    
    tipos = ["VENTA", "RESERVA", "CANCELACION", "CAMBIO_ESTATUS", 
             "REGISTRO_USUARIO", "MEMBRESIA"]
    
    total = 0
    for tipo in tipos:
        rows = session.execute(
            """SELECT event_timestamp, user_username, description 
               FROM bitacora_eventos 
               WHERE event_year = %s AND event_month = %s AND event_type = %s""",
            (year, month, tipo)
        )
        
        count = 0
        for row in rows:
            count += 1
        
        if count > 0:
            print(f"  {tipo:<20}: {count} eventos")
            total += count
    
    print(f"\n  Total eventos en {month}/{year}: {total}")


def consulta_9_historial_obra(session, artwork_id):
    """
    Q9: Historial completo de cambios de estatus de una obra.
    
    Tabla: historial_estatus_obra
    Partition Key: (artwork_id)
    
    CQL equivalente:
        SELECT * FROM historial_estatus_obra WHERE artwork_id = ?;
    """
    separador(f"Q9: Historial de estatus de la obra #{artwork_id}")
    
    rows = session.execute(
        "SELECT * FROM historial_estatus_obra WHERE artwork_id = %s",
        (artwork_id,)
    )
    
    titulo = None
    count = 0
    for row in rows:
        count += 1
        if not titulo:
            titulo = row.artwork_title
        print(f"  {row.change_timestamp.strftime('%Y-%m-%d %H:%M')} | "
              f"{row.old_status:<12} → {row.new_status:<12} | "
              f"por {row.changed_by}")
        if row.reason:
            print(f"  {'':>19} └─ {row.reason}")
    
    if count == 0:
        print(f"  (No hay historial para la obra #{artwork_id})")
    else:
        print(f"\n  Obra: {titulo}")
        print(f"  Total cambios: {count}")


def consulta_10_obras_vendidas_periodo(session, year_start, month_start, year_end, month_end):
    """
    Q10: Lista de obras vendidas en un período con detalle completo.
    
    Usa ventas_por_mes iterando meses del rango.
    Equivale al reporte "Listado de obras vendidas en un período" del Sprint 0.
    """
    separador(f"Q10: Obras vendidas del {month_start}/{year_start} al {month_end}/{year_end}")
    
    print(f"  {'ID':<5} {'Fecha':<12} {'Obra':<30} {'Artista':<20} {'Género':<12} "
          f"{'Comprador':<18} {'Total':>12}")
    print(f"  {'─'*115}")
    
    total = Decimal('0')
    count = 0
    year, month = year_start, month_start
    
    while (year, month) <= (year_end, month_end):
        rows = session.execute(
            """SELECT sale_id, sale_date, artwork_title, artist_name, genre_name,
                      buyer_username, total
               FROM ventas_por_mes WHERE year = %s AND month = %s""",
            (year, month)
        )
        
        for row in rows:
            count += 1
            total += row.total
            print(f"  {row.sale_id:<5} {row.sale_date.strftime('%Y-%m-%d'):<12} "
                  f"{row.artwork_title[:28]:<30} {row.artist_name[:18]:<20} "
                  f"{row.genre_name[:10]:<12} {row.buyer_username[:16]:<18} "
                  f"${row.total:>10,.2f}")
        
        month += 1
        if month > 12:
            month = 1
            year += 1
    
    print(f"\n  {'─'*115}")
    print(f"  Total obras vendidas: {count}")
    print(f"  Facturación total:    ${total:>12,.2f}")


# ════════════════════════════════════════════════════════════════════════════
# EJECUCIÓN PRINCIPAL
# ════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("  Sprint 2 — Consultas Gerenciales (Apache Cassandra)")
    print("  Museo de Arte Contemporáneo")
    print("=" * 70)
    
    session = get_session()
    
    # Artistas y géneros conocidos (del catálogo del museo)
    artistas = ["Pablo Picasso", "Salvador Dalí", "Frida Kahlo", 
                "Diego Rivera", "Joan Miró"]
    generos = ["Pintura", "Escultura", "Fotografía", "Cerámica", "Orfebrería"]
    
    # ── BLOQUE 1: Consultas de Facturación ──
    print("\n\n" + "▓" * 70)
    print("  BLOQUE 1: CONSULTAS DE FACTURACIÓN")
    print("▓" * 70)
    
    # Q1: Facturación de un mes específico
    consulta_1_facturacion_mensual(session, 2025, 3)
    
    # Q2: Facturación de un período (enero a junio 2025)
    consulta_2_facturacion_periodo(session, 2025, 1, 2025, 6)
    
    # Q3: Ventas de un artista
    consulta_3_ventas_por_artista(session, "Pablo Picasso")
    consulta_3_ventas_por_artista(session, "Salvador Dalí")
    
    # Q4: Ventas de un género
    consulta_4_ventas_por_genero(session, "Pintura")
    
    # Q5: Ranking de artistas
    consulta_5_ranking_artistas(session, artistas)
    
    # Q6: Ranking de géneros
    consulta_6_ranking_generos(session, generos)
    
    # ── BLOQUE 2: Consultas de Auditoría ──
    print("\n\n" + "▓" * 70)
    print("  BLOQUE 2: CONSULTAS DE AUDITORÍA Y BITÁCORA")
    print("▓" * 70)
    
    # Q7: Eventos por tipo
    consulta_7_bitacora_por_tipo(session, "VENTA", 2025, 3)
    consulta_7_bitacora_por_tipo(session, "RESERVA", 2025, 3)
    consulta_7_bitacora_por_tipo(session, "CAMBIO_ESTATUS", 2025, 3)
    
    # Q8: Resumen de todos los eventos del mes
    consulta_8_todos_los_eventos_mes(session, 2025, 3)
    consulta_8_todos_los_eventos_mes(session, 2025, 1)
    
    # Q9: Historial de estatus de obras específicas
    consulta_9_historial_obra(session, 1)   # Guernica
    consulta_9_historial_obra(session, 5)   # Cabeza de Toro
    
    # Q10: Listado de obras vendidas en un período
    consulta_10_obras_vendidas_periodo(session, 2025, 1, 2025, 6)
    
    close()
    
    print(f"\n{'='*70}")
    print("  ✓ Todas las consultas ejecutadas exitosamente")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()
