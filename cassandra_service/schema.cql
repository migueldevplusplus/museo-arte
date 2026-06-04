-- ============================================================================
-- Sprint 2 — Museo de Arte Contemporáneo
-- Modelo de Familias de Columnas (Apache Cassandra)
-- ============================================================================
-- PRINCIPIO DE DISEÑO: Query-Driven Modeling
-- Cada tabla está diseñada para responder UNA consulta frecuente del
-- administrador. Se desnormalizan datos a propósito para evitar JOINs
-- (que Cassandra no soporta).
-- ============================================================================

-- ────────────────────────────────────────────────────────────────────────────
-- 1. KEYSPACE
-- ────────────────────────────────────────────────────────────────────────────
-- SimpleStrategy con RF=1 para desarrollo local (un solo nodo Docker).
-- En producción se usaría NetworkTopologyStrategy con RF=3.

CREATE KEYSPACE IF NOT EXISTS museo
WITH replication = {
    'class': 'SimpleStrategy',
    'replication_factor': 1
};

USE museo;

-- ────────────────────────────────────────────────────────────────────────────
-- 2. TABLAS DE FACTURACIÓN (Resúmenes gerenciales)
-- ────────────────────────────────────────────────────────────────────────────

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ TABLA 1: ventas_por_mes                                                 ║
-- ║ Consulta: "¿Cuánto se facturó en el mes X del año Y?"                   ║
-- ║ Partition Key: (year, month) → agrupa ventas del mismo mes              ║
-- ║ Clustering: sale_date DESC, sale_id → orden cronológico inverso         ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

CREATE TABLE IF NOT EXISTS ventas_por_mes (
    year             INT,
    month            INT,
    sale_date        TIMESTAMP,
    sale_id          INT,
    artwork_id       INT,
    artwork_title    TEXT,
    artist_name      TEXT,
    genre_name       TEXT,
    buyer_username   TEXT,
    payment_method   TEXT,
    subtotal         DECIMAL,
    iva              DECIMAL,
    commission       DECIMAL,
    total            DECIMAL,
    PRIMARY KEY ((year, month), sale_date, sale_id)
) WITH CLUSTERING ORDER BY (sale_date DESC, sale_id DESC)
   AND comment = 'Resumen de facturación mensual. PK compuesta: año+mes particiona, fecha ordena.';


-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ TABLA 2: ventas_por_artista                                             ║
-- ║ Consulta: "¿Cuáles son todas las ventas del artista X?"                 ║
-- ║ Partition Key: (artist_name) → todas las ventas de un artista juntas    ║
-- ║ Clustering: sale_date DESC, sale_id                                     ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

CREATE TABLE IF NOT EXISTS ventas_por_artista (
    artist_name      TEXT,
    sale_date        TIMESTAMP,
    sale_id          INT,
    artwork_id       INT,
    artwork_title    TEXT,
    genre_name       TEXT,
    buyer_username   TEXT,
    payment_method   TEXT,
    subtotal         DECIMAL,
    iva              DECIMAL,
    commission       DECIMAL,
    total            DECIMAL,
    PRIMARY KEY ((artist_name), sale_date, sale_id)
) WITH CLUSTERING ORDER BY (sale_date DESC, sale_id DESC)
   AND comment = 'Ventas agrupadas por artista para reportes de comisiones.';


-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ TABLA 3: ventas_por_genero                                              ║
-- ║ Consulta: "¿Cuáles son las ventas del género X?"                        ║
-- ║ Partition Key: (genre_name) → todas las ventas de un género juntas      ║
-- ║ Clustering: sale_date DESC, sale_id                                     ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

CREATE TABLE IF NOT EXISTS ventas_por_genero (
    genre_name       TEXT,
    sale_date        TIMESTAMP,
    sale_id          INT,
    artwork_id       INT,
    artwork_title    TEXT,
    artist_name      TEXT,
    buyer_username   TEXT,
    payment_method   TEXT,
    subtotal         DECIMAL,
    iva              DECIMAL,
    commission       DECIMAL,
    total            DECIMAL,
    PRIMARY KEY ((genre_name), sale_date, sale_id)
) WITH CLUSTERING ORDER BY (sale_date DESC, sale_id DESC)
   AND comment = 'Ventas agrupadas por género artístico para análisis de tendencias.';


-- ────────────────────────────────────────────────────────────────────────────
-- 3. TABLAS DE AUDITORÍA (Bitácora inmutable)
-- ────────────────────────────────────────────────────────────────────────────

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ TABLA 4: bitacora_eventos                                               ║
-- ║ Consulta: "¿Qué eventos de tipo X ocurrieron?"                          ║
-- ║ Partition Key: (event_year, event_month, event_type) → evita            ║
-- ║   particiones infinitamente grandes agrupando por mes+tipo              ║
-- ║ Clustering: event_timestamp DESC, event_id → orden cronológico          ║
-- ║                                                                         ║
-- ║ Tipos de evento: VENTA, RESERVA, CANCELACION, CAMBIO_ESTATUS,          ║
-- ║                  REGISTRO_USUARIO, MEMBRESIA                            ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

CREATE TABLE IF NOT EXISTS bitacora_eventos (
    event_year       INT,
    event_month      INT,
    event_type       TEXT,
    event_timestamp  TIMESTAMP,
    event_id         UUID,
    user_username    TEXT,
    description      TEXT,
    entity_type      TEXT,
    entity_id        TEXT,
    old_value        TEXT,
    new_value        TEXT,
    PRIMARY KEY ((event_year, event_month, event_type), event_timestamp, event_id)
) WITH CLUSTERING ORDER BY (event_timestamp DESC, event_id DESC)
   AND comment = 'Bitácora inmutable de eventos de seguridad y operaciones del museo.';


-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ TABLA 5: historial_estatus_obra                                         ║
-- ║ Consulta: "¿Cuál es el historial de cambios de estatus de la obra X?"   ║
-- ║ Partition Key: (artwork_id) → todo el historial de una obra junto       ║
-- ║ Clustering: change_timestamp DESC → más reciente primero                ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

CREATE TABLE IF NOT EXISTS historial_estatus_obra (
    artwork_id       INT,
    change_timestamp TIMESTAMP,
    artwork_title    TEXT,
    old_status       TEXT,
    new_status       TEXT,
    changed_by       TEXT,
    reason           TEXT,
    PRIMARY KEY ((artwork_id), change_timestamp)
) WITH CLUSTERING ORDER BY (change_timestamp DESC)
   AND comment = 'Historial de cambios de estatus por obra (AVAILABLE→RESERVED→SOLD).';
