# Sprint 2 — Históricos, Auditoría y Reportes (Apache Cassandra)

Documentación del trabajo realizado en el marco del **Proyecto Académico: Plataforma Políglota para el Museo de Arte Contemporáneo**.

---

## 1. Contexto del proyecto completo

| Capa | Tecnología | Rol |
|------|------------|-----|
| **Core transaccional (SBD I)** | Django + MySQL | Usuarios, reservas, ventas, facturación, membresías — datos ACID |
| **Sprint 1 — Catálogo** | MongoDB | Obras y metadatos flexibles por género |
| **Sprint 2 — Históricos** | **Apache Cassandra** | **Resúmenes de facturación, bitácora de auditoría, historial de estatus** |
| Sprints futuros | Neo4j, APIs/microservicios | Recomendaciones, integración |

El Sprint 2 añade una capa de **alta disponibilidad y lectura optimizada** para datos históricos y de auditoría que no requieren transaccionalidad ACID.

---

## 2. Objetivo del Sprint 2

> Diseñar familias de columnas con **Query-Driven Modeling**, mantener una **bitácora inmutable** de eventos de seguridad y generar **resúmenes de facturación masivos**, definiendo correctamente las Partition Keys y Clustering Columns.

**Duración prevista:** semanas 3–4.

---

## 3. ¿Por qué Cassandra?

| Necesidad del museo | Capacidad de Cassandra |
|--------------------|-----------------------|
| Resúmenes de facturación de millones de ventas | Lecturas O(1) por partition key |
| Bitácora inmutable de eventos | Modelo append-only, no hay UPDATE/DELETE semántico obligatorio |
| Alta disponibilidad (el administrador siempre puede consultar) | Arquitectura masterless, tolerante a fallos |
| Consultas predecibles (siempre "por mes", "por artista", etc.) | Query-Driven Modeling: cada tabla = una consulta |

**Cassandra NO es adecuado para:** JOINs, transacciones multi-tabla, consultas ad-hoc no planificadas. Esas necesidades las cubre MySQL (core transaccional).

---

## 4. Diseño de Familias de Columnas

### 4.1 Principio: Query-Driven Modeling

En Cassandra **la consulta dicta el modelo**. No se normaliza como en relacional; se **desnormalizan** datos para que cada tabla responda a exactamente una consulta frecuente del administrador sin necesidad de JOINs.

### 4.2 Keyspace

```cql
CREATE KEYSPACE IF NOT EXISTS museo
WITH replication = {
    'class': 'SimpleStrategy',
    'replication_factor': 1
};
```

- `SimpleStrategy` con RF=1 para desarrollo local (un solo nodo Docker).
- En producción se usaría `NetworkTopologyStrategy` con RF=3.

### 4.3 Tablas diseñadas

Se definieron **5 familias de columnas**, cada una optimizada para una consulta gerencial:

---

#### TABLA 1: `ventas_por_mes` — Facturación mensual

**Consulta que responde:** *"¿Cuánto se facturó en el mes X del año Y?"*

```
┌─────────────────────────────────────────────────────┐
│ Partition Key:  (year, month)                       │
│ Clustering:     sale_date DESC, sale_id DESC        │
│                                                     │
│ Justificación:                                      │
│ - PK agrupa todas las ventas de un mes              │
│ - sale_date DESC: las más recientes primero         │
│ - sale_id: desambigua ventas en el mismo instante   │
│ - Datos desnormalizados: artwork, artist, genre     │
│   embebidos para evitar JOINs                       │
└─────────────────────────────────────────────────────┘
```

```cql
CREATE TABLE ventas_por_mes (
    year INT, month INT,              -- Partition Key
    sale_date TIMESTAMP, sale_id INT, -- Clustering Columns
    artwork_id INT, artwork_title TEXT,
    artist_name TEXT, genre_name TEXT,
    buyer_username TEXT, payment_method TEXT,
    subtotal DECIMAL, iva DECIMAL,
    commission DECIMAL, total DECIMAL,
    PRIMARY KEY ((year, month), sale_date, sale_id)
) WITH CLUSTERING ORDER BY (sale_date DESC, sale_id DESC);
```

**Ejemplo CQL:**
```cql
SELECT * FROM ventas_por_mes WHERE year = 2025 AND month = 6;
```

---

#### TABLA 2: `ventas_por_artista` — Ventas por artista

**Consulta que responde:** *"¿Cuáles son todas las ventas del artista Picasso?"*

```
┌─────────────────────────────────────────────────────┐
│ Partition Key:  (artist_name)                       │
│ Clustering:     sale_date DESC, sale_id DESC        │
│                                                     │
│ Justificación:                                      │
│ - PK agrupa todas las ventas de un artista          │
│ - Permite calcular comisiones y rankings            │
└─────────────────────────────────────────────────────┘
```

```cql
CREATE TABLE ventas_por_artista (
    artist_name TEXT,                 -- Partition Key
    sale_date TIMESTAMP, sale_id INT, -- Clustering Columns
    artwork_id INT, artwork_title TEXT,
    genre_name TEXT, buyer_username TEXT,
    payment_method TEXT,
    subtotal DECIMAL, iva DECIMAL,
    commission DECIMAL, total DECIMAL,
    PRIMARY KEY ((artist_name), sale_date, sale_id)
) WITH CLUSTERING ORDER BY (sale_date DESC, sale_id DESC);
```

**Ejemplo CQL:**
```cql
SELECT * FROM ventas_por_artista WHERE artist_name = 'Pablo Picasso';
```

---

#### TABLA 3: `ventas_por_genero` — Ventas por género artístico

**Consulta que responde:** *"¿Cuáles son las ventas de Pinturas?"*

```
┌─────────────────────────────────────────────────────┐
│ Partition Key:  (genre_name)                        │
│ Clustering:     sale_date DESC, sale_id DESC        │
│                                                     │
│ Justificación:                                      │
│ - PK agrupa ventas por tipo de arte                 │
│ - Permite análisis de tendencias del mercado        │
└─────────────────────────────────────────────────────┘
```

```cql
SELECT * FROM ventas_por_genero WHERE genre_name = 'Pintura';
```

---

#### TABLA 4: `bitacora_eventos` — Auditoría de seguridad

**Consulta que responde:** *"¿Qué eventos de tipo VENTA ocurrieron en marzo 2025?"*

```
┌─────────────────────────────────────────────────────┐
│ Partition Key:  (event_year, event_month, event_type)│
│ Clustering:     event_timestamp DESC, event_id DESC │
│                                                     │
│ Justificación:                                      │
│ - PK compuesta año+mes+tipo evita particiones       │
│   infinitamente grandes (bounded growth)            │
│ - event_id UUID evita colisiones en mismo timestamp │
│ - Inmutable: solo INSERT, nunca UPDATE/DELETE        │
│                                                     │
│ Tipos de evento:                                    │
│   VENTA, RESERVA, CANCELACION, CAMBIO_ESTATUS,     │
│   REGISTRO_USUARIO, MEMBRESIA                       │
└─────────────────────────────────────────────────────┘
```

```cql
CREATE TABLE bitacora_eventos (
    event_year INT, event_month INT,  -- ┐
    event_type TEXT,                   -- ┘ Partition Key
    event_timestamp TIMESTAMP,        -- ┐
    event_id UUID,                    -- ┘ Clustering Columns
    user_username TEXT, description TEXT,
    entity_type TEXT, entity_id TEXT,
    old_value TEXT, new_value TEXT,
    PRIMARY KEY ((event_year, event_month, event_type), event_timestamp, event_id)
) WITH CLUSTERING ORDER BY (event_timestamp DESC, event_id DESC);
```

**Ejemplo CQL:**
```cql
SELECT * FROM bitacora_eventos 
WHERE event_year = 2025 AND event_month = 3 AND event_type = 'VENTA';
```

---

#### TABLA 5: `historial_estatus_obra` — Trazabilidad de estatus

**Consulta que responde:** *"¿Cuál es el historial de cambios de la obra #1?"*

```
┌─────────────────────────────────────────────────────┐
│ Partition Key:  (artwork_id)                        │
│ Clustering:     change_timestamp DESC               │
│                                                     │
│ Justificación:                                      │
│ - PK agrupa todo el historial de una obra           │
│ - Trazabilidad: AVAILABLE → RESERVED → SOLD         │
│ - Registra quién hizo cada cambio y por qué         │
└─────────────────────────────────────────────────────┘
```

```cql
SELECT * FROM historial_estatus_obra WHERE artwork_id = 1;
```

---

## 5. Arquitectura de archivos del Sprint 2

```
museo-arte/
├── docker-compose.cassandra.yml      ← Infraestructura Cassandra (Docker)
├── .env                              ← Variables de conexión Cassandra agregadas
└── cassandra_service/                ← Microservicio/módulo de Cassandra
    ├── __init__.py
    ├── db_cassandra.py               ← Conexión al cluster (cassandra-driver)
    ├── schema.cql                    ← DDL: Keyspace + 5 tablas
    ├── crear_esquema.py              ← Ejecuta schema.cql desde Python
    ├── seed_cassandra.py             ← Datos de prueba (15 ventas, 60+ eventos)
    ├── migrar_mysql_a_cassandra.py   ← ETL: MySQL → Cassandra (datos reales)
    └── consultas_cassandra.py        ← 10 consultas gerenciales CQL
```

---

## 6. Cómo levantar y ejecutar

### Requisitos previos
- Docker instalado
- Python 3.10+
- Dependencia: `pip install cassandra-driver`

### Paso a paso

```bash
# 1. Levantar Cassandra con Docker (desde la raíz del proyecto)
docker compose -f docker-compose.cassandra.yml up -d

# 2. Esperar ~60 segundos a que Cassandra esté lista
#    Verificar con:
docker exec -it museo-cassandra cqlsh -e "DESCRIBE KEYSPACES;"

# 3. Crear el esquema (keyspace + tablas)
python -m cassandra_service.crear_esquema

# 4a. Insertar datos de prueba (sin depender de MySQL)
python -m cassandra_service.seed_cassandra

# 4b. O migrar datos reales desde MySQL
python -m cassandra_service.migrar_mysql_a_cassandra

# 5. Ejecutar las consultas gerenciales
python -m cassandra_service.consultas_cassandra
```

### Verificar manualmente con cqlsh

```bash
docker exec -it museo-cassandra cqlsh

# Dentro de cqlsh:
USE museo;
DESCRIBE TABLES;
SELECT COUNT(*) FROM ventas_por_mes;
SELECT * FROM ventas_por_mes WHERE year = 2025 AND month = 3;
SELECT * FROM bitacora_eventos WHERE event_year = 2025 AND event_month = 3 AND event_type = 'VENTA';
SELECT * FROM historial_estatus_obra WHERE artwork_id = 1;
```

---

## 7. Consultas implementadas

### Bloque 1: Facturación

| # | Consulta | Tabla | CQL |
|---|----------|-------|-----|
| Q1 | Facturación de un mes | `ventas_por_mes` | `WHERE year=? AND month=?` |
| Q2 | Facturación de un período (rango de meses) | `ventas_por_mes` | Iteración mes a mes |
| Q3 | Ventas de un artista específico | `ventas_por_artista` | `WHERE artist_name=?` |
| Q4 | Ventas de un género específico | `ventas_por_genero` | `WHERE genre_name=?` |
| Q5 | Ranking de artistas por facturación | `ventas_por_artista` | Iteración por artista |
| Q6 | Ranking de géneros por facturación | `ventas_por_genero` | Iteración por género |

### Bloque 2: Auditoría

| # | Consulta | Tabla | CQL |
|---|----------|-------|-----|
| Q7 | Eventos por tipo en un mes | `bitacora_eventos` | `WHERE event_year=? AND event_month=? AND event_type=?` |
| Q8 | Resumen de todos los eventos del mes | `bitacora_eventos` | Iteración por tipo |
| Q9 | Historial de estatus de una obra | `historial_estatus_obra` | `WHERE artwork_id=?` |
| Q10 | Listado de obras vendidas en período | `ventas_por_mes` | Iteración mes a mes |

---

## 8. Coexistencia MySQL ↔ Cassandra

| Aspecto | MySQL (Core) | Cassandra (Sprint 2) |
|---------|-------------|---------------------|
| **Rol** | Origen de verdad transaccional (ACID) | Almacén de lectura optimizado para reportes |
| **Escritura** | Ventas, reservas, CRUD | Recibe datos migrados/replicados |
| **Lectura** | Operaciones en tiempo real | Consultas gerenciales masivas |
| **Consistencia** | Strong consistency | Eventual consistency (aceptable para reportes) |
| **Modelo** | Normalizado (3FN) | Desnormalizado (Query-Driven) |

**Flujo de datos (Sprint 4 - Integración):**
```
MySQL (venta procesada) → [evento/señal] → Cassandra (registro en tablas de reporte)
```
En este Sprint 2 la migración se ejecuta manualmente. La integración automática se implementará en el Sprint 4.

---

## 9. Datos de prueba (seed)

El script `seed_cassandra.py` genera:
- **15 ventas** de obras distribuidas en 6 meses (enero–junio 2025)
- **5 artistas**: Picasso, Dalí, Kahlo, Rivera, Miró
- **5 géneros**: Pintura, Escultura, Fotografía, Cerámica, Orfebrería
- **65+ eventos de auditoría**: ventas, reservas, cambios de estatus, registros de usuario, membresías, cancelaciones
- **30 registros de historial de estatus**: transiciones AVAILABLE→RESERVED→SOLD

---

## 10. Relación con roles del equipo

| Rol académico | Trabajo observable en el repo |
|---------------|-------------------------------|
| **Ingeniero de Datos / Series Temporales (Cassandra)** | Diseño de 5 familias de columnas, PK/CK, schema.cql, scripts de inserción y consultas |
| DBA Relacional | Modelo Django/MySQL fuente de la migración |
| Arquitecto de integración | Pendiente Sprint 4: señales Django → Cassandra |

---

## 11. Justificación de decisiones de diseño

### ¿Por qué 3 tablas de ventas en vez de 1?
Cassandra no soporta JOINs ni índices secundarios eficientes. Tener `ventas_por_mes`, `ventas_por_artista` y `ventas_por_genero` **es el patrón correcto** en Cassandra: se duplican datos para que cada consulta sea O(1) por partition key. El trade-off (espacio extra) es aceptable dado que las ventas de un museo son un volumen manejable.

### ¿Por qué la bitácora tiene (year, month, type) como Partition Key?
Si usáramos solo `event_type`, la partición de "VENTA" crecería infinitamente. Al agregar `year + month`, cada partición está **acotada** (bounded partition) al número de eventos de un tipo en un mes — un patrón recomendado para time-series en Cassandra.

### ¿Por qué UUID en event_id?
Evita colisiones cuando dos eventos ocurren en el mismo timestamp exacto. Es el patrón estándar para logs en Cassandra.

### ¿Por qué Clustering Order DESC?
Los administradores siempre quieren ver primero lo más reciente. `DESC` evita un `ORDER BY` en la consulta, que Cassandra ejecuta eficientemente solo en el orden del clustering definido en la tabla.

---

## 12. Limitaciones y trabajo futuro

1. **Integración automática (Sprint 4):** Actualmente la migración es manual. En el Sprint 4 se conectará vía señales Django para que cada venta se registre automáticamente en Cassandra.
2. **Un solo nodo:** En producción se usaría un cluster de al menos 3 nodos con RF=3.
3. **TTL para datos antiguos:** Se podría agregar `USING TTL` para expirar automáticamente datos de auditoría después de N años.
4. **Tablas materializadas:** Para rankings globales (top artistas de todos los tiempos), se podría crear una tabla materializada adicional.
