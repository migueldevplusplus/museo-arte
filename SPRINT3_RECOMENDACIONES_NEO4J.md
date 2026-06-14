# Sprint 3 — Recomendaciones y Red de Conocimiento (Neo4j)

Documentación del trabajo realizado en el marco del **Proyecto Académico: Plataforma Políglota para el Museo de Arte Contemporáneo**.

---

## 1. Contexto del proyecto completo

| Capa | Tecnología | Rol |
|------|------------|-----|
| **Core transaccional (SBD I)** | Django + MySQL | Usuarios, reservas, ventas, facturación, membresías — datos ACID |
| **Sprint 1 — Catálogo** | MongoDB | Obras y metadatos flexibles por género |
| **Sprint 2 — Históricos** | Apache Cassandra | Resúmenes de facturación, bitácora de auditoría, historial de estatus |
| **Sprint 3 — Recomendaciones** | **Neo4j** | **Red de conocimiento, recomendaciones de obras, artistas similares** |

El Sprint 3 añade una capa de **grafos** para modelar las relaciones entre compradores, obras, artistas y géneros, permitiendo consultas de recomendación basadas en la estructura de la red.

---

## 2. Objetivo del Sprint 3

> Diseñar un modelo de grafo que represente el conocimiento del museo (quiénes compran qué, quién crea qué, en qué géneros trabajan los artistas), migrar los datos relacionales a Neo4j, y desarrollar 5 consultas Cypher de recomendación avanzada.

**Duración prevista:** semanas 5–6.

---

## 3. ¿Por qué Neo4j?

| Necesidad del museo | Capacidad de Neo4j |
|--------------------|--------------------|
| Recomendar obras del mismo género que el usuario ya compró | Recorrido eficiente por relaciones en el grafo (obras → artista → género → otras obras) |
| Encontrar artistas similares que compartan géneros | Patrón "amigos en común" sobre el grafo (artista → género → otro artista) |
| Consultas que cruzan múltiples entidades en un solo paso | Cypher expresa joins implícitos mediante patrones de relación |
| Excluir obras ya compradas de las recomendaciones | Filtro directo con `NOT (b)-[:BOUGHT]->(rec)` |
| Escalabilidad para un catálogo en crecimiento | Navegación por relaciones sin JOINs costosos |

**Neo4j NO es adecuado para:** transacciones ACID pesadas, joins tabulares, consultas agregadas masivas. Esas necesidades las cubren MySQL y Cassandra.

---

## 4. Modelo del grafo

### 4.1 Diagrama visual

```
                    ┌─────────────────────────────────────┐
                    │         MODELO DEL GRAFO NEO4J       │
                    │   (Red de conocimiento del museo)    │
                    └─────────────────────────────────────┘

    (Buyer) ──[:BOUGHT]──> (Artwork) <──[:CREATED]── (Artist)
       │                        │                            │
       │                        │                       [:WORKS_IN]
       │                        │                            │
       │                   (genre_name)                      │
       │                   (propiedad)                       v
       │                                                  (Genre)
       └─────────────────────────────────────────────────────┘
               (un Buyer puede comprar muchas obras)

    Nodos:       4 tipos (Buyer, Artwork, Artist, Genre)
    Relaciones:  3 tipos (BOUGHT, CREATED, WORKS_IN)
```

### 4.2 Descripción de nodos

```
(:Buyer)
  ├── id          (INT, UNIQUE)      ← ID desde MySQL
  ├── username    (STRING, INDEX)    ← Nombre de usuario
  └── email       (STRING)           ← Correo electrónico

(:Artwork)
  ├── id          (INT, UNIQUE)      ← ID desde MySQL
  ├── title       (STRING, INDEX)    ← Título de la obra
  ├── price       (FLOAT)            ← Precio actual
  ├── status      (STRING)           ← AVAILABLE / RESERVED / SOLD
  ├── genre_name  (STRING, INDEX)    ← Nombre del género (desnormalizado)
  └── creation_date (STRING)         ← Fecha de creación

(:Artist)
  ├── id          (INT, UNIQUE)      ← ID desde MySQL
  ├── name        (STRING, INDEX)    ← Nombre del artista
  └── nationality (STRING)           ← Nacionalidad

(:Genre)
  └── name        (STRING, UNIQUE)   ← Nombre del género (Pintura, Escultura...)
```

### 4.3 Descripción de relaciones

```
(b:Buyer)-[:BOUGHT]->(aw:Artwork)
  └── Significado: El comprador b adquirió la obra aw.
  └── Cardinalidad: Un Buyer puede tener 0, 1 o N BOUGHT.

(a:Artist)-[:CREATED]->(aw:Artwork)
  └── Significado: El artista a creó la obra aw.
  └── Cardinalidad: Un Artist puede tener 1 o N CREATED.

(a:Artist)-[:WORKS_IN]->(g:Genre)
  └── Significado: El artista a trabaja en el género g.
  └── Cardinalidad: Un Artist puede trabajar en 1 o N géneros.
```

### 4.4 Justificación del modelo

**genre_name desnormalizado en Artwork:**
Se almacena `genre_name` directamente como propiedad del nodo `Artwork` (además de existir como nodo `Genre`). Esto permite consultar obras del mismo género sin necesidad de atravesar dos relaciones (`Artwork → Artist → Genre → Artist → Artwork`), resultando en queries más simples y rápidas para el caso de uso principal (recomendaciones por género).

**IDs de MySQL como propiedad única:**
Cada nodo conserva su `id` original de MySQL como identificador único (`REQUIRE b.id IS UNIQUE`). Esto permite la trazabilidad con el core transaccional y evita duplicados durante la migración con `MERGE`.

---

## 5. Arquitectura de archivos

```
museo-arte/
├── docker-compose.neo4j.yml           ← Infraestructura Neo4j (Docker)
├── .env                                ← Variables de conexión Neo4j agregadas
├── requirements.txt                    ← neo4j, mysql-connector-python
└── neo4j_service/                      ← Módulo de integración con Neo4j
    ├── __init__.py
    ├── db_neo4j.py                     ← Conexión singleton al driver Bolt
    ├── schema.cypher                   ← DDL: constraints + índices
    ├── crear_esquema.py                ← Ejecuta schema.cypher desde Python
    ├── seed_neo4j.py                   ← Datos sintéticos de prueba
    ├── migrar_mysql_a_neo4j.py         ← ETL: MySQL → Neo4j (datos reales)
    └── consultas_neo4j.py              ← 5 consultas Cypher + menú interactivo

museum/
├── views_neo4j.py                      ← 6 vistas Django (protegidas staff/employee)
└── urls.py                             ← 6 rutas Neo4j agregadas

templates/
├── base.html                           ← Enlace "Recomendaciones Neo4j" en navbar
└── museum/neo4j/                       ← Plantillas de los reportes
    ├── base_neo4j.html                 ← Sidebar de navegación (tema verde)
    ├── recomendaciones.html            ← Q1: por usuario
    ├── mismo_artista.html              ← Q2: por usuario
    ├── obras_relacionadas.html         ← Q3: por obra
    ├── artistas_similares.html         ← Q4: por artista
    └── compradores_por_genero.html     ← Q5: por género
```

### Módulo neo4j_service/

| Archivo | Función |
|---------|---------|
| `__init__.py` | Convierte el directorio en paquete Python |
| `db_neo4j.py` | Singleton que expone `get_driver()` y `close()` | conexión Bolt con credenciales de `.env` |
| `schema.cypher` | 4 constraints UNIQUE + 4 índices para optimizar consultas |
| `crear_esquema.py` | Ejecuta las sentencias del schema.cypher contra Neo4j |
| `seed_neo4j.py` | Población sintética: 5 géneros, 5 artistas, 6 obras, 3 compradores, 4 compras |
| `migrar_mysql_a_neo4j.py` | ETL completo: extrae de MySQL y hace MERGE en Neo4j |
| `consultas_neo4j.py` | 5 funciones de consulta + menú interactivo por terminal |

### Capa web (Django)

| Archivo | Función |
|---------|---------|
| `museum/views_neo4j.py` | 6 vistas protegidas que ejecutan Cypher y renderizan templates |
| `museum/urls.py` | 6 rutas bajo `/neo4j/`: dashboard, recomendaciones, mismo-artista, obras-relacionadas, artistas-similares, compradores-genero |
| `templates/base.html` | Enlace en navbar → `/neo4j/` |
| `templates/museum/neo4j/base_neo4j.html` | Layout base con sidebar verde para los 5 reportes |
| `templates/museum/neo4j/*.html` | 5 templates de reporte con formularios y tablas |

### Infraestructura

| Archivo | Función |
|---------|---------|
| `docker-compose.neo4j.yml` | Contenedor Neo4j 5-community con APOC, puertos 7687 (Bolt) y 7474 (Browser) |
| `.env` | Variables `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` |
| `requirements.txt` | Dependencias `neo4j==5.27.0` y `mysql-connector-python==9.2.0` |

---

## 6. Cómo levantar y ejecutar

### Requisitos previos

- Docker instalado
- Python 3.10+
- Dependencias: `pip install -r requirements.txt`

### Paso a paso

```bash
# 1. Levantar Neo4j con Docker (desde la raíz del proyecto)
docker compose -f docker-compose.neo4j.yml up -d

# 2. Verificar que el contenedor esté corriendo
docker ps | grep museo-neo4j

# 3. Crear el esquema (constraints + índices)
python -m neo4j_service.crear_esquema

# 4a. Insertar datos de prueba (sin depender de MySQL)
python -m neo4j_service.seed_neo4j

# 4b. O migrar datos reales desde MySQL
python -m neo4j_service.migrar_mysql_a_neo4j

# 5. Probar las consultas por terminal
python -m neo4j_service.consultas_neo4j

# 6. Iniciar Django y abrir el navegador en /neo4j/
python manage.py runserver
# http://127.0.0.1:8000/neo4j/
```

### Verificar manualmente con Neo4j Browser

```
Abrir http://localhost:7474 en el navegador
Usuario: neo4j
Contraseña: password
```

**Consultas de verificación:**

```cypher
// Ver nodos por tipo
MATCH (b:Buyer) RETURN count(b) AS buyers;
MATCH (a:Artist) RETURN count(a) AS artists;
MATCH (aw:Artwork) RETURN count(aw) AS artworks;
MATCH (g:Genre) RETURN count(g) AS genres;

// Ver relaciones
MATCH ()-[r:BOUGHT]->() RETURN count(r) AS purchases;
MATCH ()-[r:CREATED]->() RETURN count(r) AS creations;
MATCH ()-[r:WORKS_IN]->() RETURN count(r) AS genres_assigned;

// Ver el grafo completo
MATCH (n) RETURN n;
```

---

## 7. Consultas implementadas

### Q1 — Recomendaciones por género

**Propósito:** Recomendar obras del mismo género que el comprador ya ha adquirido, excluyendo las que ya compró.

**Cypher:**

```cypher
MATCH (b:Buyer {username:$u})-[:BOUGHT]->(a:Artwork)
WITH b, collect(DISTINCT a.genre_name) AS genres
MATCH (other:Artist)-[:CREATED]->(rec:Artwork)
WHERE rec.genre_name IN genres
  AND NOT (b)-[:BOUGHT]->(rec)
RETURN DISTINCT rec.title AS obra, rec.price AS precio,
       other.name AS artista, rec.genre_name AS genero
ORDER BY rec.price DESC
```

**Explicación:**
1. Encuentra las obras que compró el usuario.
2. Recolecta los géneros **distintos** de esas obras.
3. Busca otras obras que pertenezcan a esos mismos géneros.
4. Excluye las que el usuario ya compró.

**Uso por terminal:** `python -m neo4j_service.consultas_neo4j` → opción 1
**Uso web:** `/neo4j/recomendaciones/` → seleccionar comprador

---

### Q2 — Obras del mismo artista

**Propósito:** Recomendar obras del mismo artista que el comprador ya ha adquirido, excluyendo las que ya compró.

**Cypher:**

```cypher
MATCH (b:Buyer {username:$u})-[:BOUGHT]->(:Artwork)<-[:CREATED]-(a:Artist)
MATCH (a)-[:CREATED]->(rec:Artwork)
WHERE NOT (b)-[:BOUGHT]->(rec)
RETURN DISTINCT rec.title AS obra, rec.price AS precio, a.name AS artista
ORDER BY rec.price DESC
```

**Explicación:**
1. Encuentra los artistas de las obras que compró el usuario.
2. Busca otras obras creadas por esos mismos artistas.
3. Excluye las que el usuario ya compró.

**Uso por terminal:** `python -m neo4j_service.consultas_neo4j` → opción 2
**Uso web:** `/neo4j/mismo-artista/` → seleccionar comprador

---

### Q3 — Obras relacionadas por género

**Propósito:** Dada una obra específica, encontrar otras obras del mismo género.

**Cypher:**

```cypher
MATCH (aw:Artwork {id:$id})
MATCH (other:Artist)-[:CREATED]->(related:Artwork {genre_name: aw.genre_name})
WHERE related.id <> $id
RETURN DISTINCT related.title AS obra, related.price AS precio,
       other.name AS artista, related.genre_name AS genero
ORDER BY related.price DESC
```

**Explicación:**
1. Encuentra la obra seleccionada por su ID.
2. Toma su propiedad `genre_name`.
3. Busca otras obras con el mismo `genre_name`.
4. Excluye la obra original.

**Uso por terminal:** `python -m neo4j_service.consultas_neo4j` → opción 3 (ID numérico)
**Uso web:** `/neo4j/obras-relacionadas/` → seleccionar obra del menú

---

### Q4 — Artistas similares

**Propósito:** Encontrar artistas que trabajan en los mismos géneros que el artista seleccionado.

**Cypher:**

```cypher
MATCH (a1:Artist {name:$name})-[:WORKS_IN]->(g:Genre)
MATCH (g)<-[:WORKS_IN]-(a2:Artist)
WHERE a1 <> a2
RETURN DISTINCT a2.name AS artista, collect(g.name) AS generos_compartidos
ORDER BY a2.name
```

**Explicación:**
1. Encuentra el artista seleccionado y los géneros en los que trabaja.
2. Busca otros artistas que trabajen en esos mismos géneros.
3. Devuelve los artistas similares y la lista de géneros que comparten.

**Uso por terminal:** `python -m neo4j_service.consultas_neo4j` → opción 4
**Uso web:** `/neo4j/artistas-similares/` → seleccionar artista

---

### Q5 — Compradores por género

**Propósito:** Listar los compradores que han adquirido obras de un género específico.

**Cypher:**

```cypher
MATCH (b:Buyer)-[:BOUGHT]->(a:Artwork)
WHERE a.genre_name = $genre
RETURN b.username AS comprador, count(a) AS obras_compradas,
       collect(a.title) AS titulos
ORDER BY obras_compradas DESC
```

**Explicación:**
1. Encuentra todas las relaciones BOUGHT que apuntan a obras del género indicado.
2. Agrupa por comprador.
3. Cuenta cuántas obras compró cada uno y lista los títulos.

**Uso por terminal:** `python -m neo4j_service.consultas_neo4j` → opción 5
**Uso web:** `/neo4j/compradores-genero/` → seleccionar género

---

## 8. Coexistencia MySQL ↔ Neo4j

| Aspecto | MySQL (Core) | Neo4j (Sprint 3) |
|---------|-------------|------------------|
| **Rol** | Origen de verdad transaccional (ACID) | Grafo de conocimiento para recomendaciones |
| **Escritura** | Ventas, reservas, CRUD de obras/usuarios | Recibe datos migrados desde MySQL |
| **Lectura** | Operaciones en tiempo real | Consultas de recomendación y redes |
| **Consistencia** | Strong consistency | Consistencia del grafo por operación |
| **Modelo** | Normalizado (3FN) — tablas y JOINs | Propiedades + relaciones — nodos y aristas |
| **Ejemplo de consulta** | `SELECT * FROM sale WHERE buyer_id = X;` | `MATCH (b:Buyer)-[:BOUGHT]->(a:Artwork) RETURN a;` |

**Flujo de datos (actual — manual):**

```
MySQL (datos existentes) → migrar_mysql_a_neo4j.py → Neo4j (grafo)
```

La migración se ejecuta manualmente con `python -m neo4j_service.migrar_mysql_a_neo4j`. La sincronización automática (vía señales Django) queda como trabajo futuro.

---

## 9. Datos de prueba (seed)

El script `seed_neo4j.py` genera un conjunto de datos sintéticos para verificar las consultas sin depender de MySQL:

| Elemento | Cantidad |
|----------|----------|
| Géneros | 5 (Pintura, Escultura, Fotografía, Cerámica, Orfebrería) |
| Artistas | 5 (Picasso, Dalí, Kahlo, Rivera, Orozco) |
| Obras | 6 (Guernica, La persistencia de la memoria, Las dos Fridas, etc.) |
| Compradores | 3 (con relaciones BOUGHT) |
| Relaciones BOUGHT | 4 (compras de ejemplo) |

La migración desde MySQL (`migrar_mysql_a_neo4j.py`) importa los datos reales del sistema (géneros, artistas, obras y ventas) usando operaciones `MERGE` para garantizar idempotencia.

---

## 10. Relación con roles del equipo

| Rol académico | Trabajo observable en el repo |
|---------------|-------------------------------|
| **Ingeniero de Grafos (Neo4j)** | Modelo del grafo (4 nodos, 3 relaciones), schema.cypher, 5 consultas Cypher, migración ETL, seed de prueba |
| **Desarrollador Full-Stack** | 6 vistas en Django, 6 rutas, 5 templates Bootstrap con sidebar, integración web de las consultas |
| **Arquitecto de integración** | Coexistencia MySQL → Neo4j con migración manual; patrón de sincronización previsto para integración futura |

---

## 11. Justificación de decisiones de diseño

### ¿Por qué `genre_name` desnormalizado en Artwork?

El caso de uso principal (Q1 y Q3) requiere encontrar obras del mismo género. Si la única vía fuera atravesar `(Artwork)<-[:CREATED]-(Artist)-[:WORKS_IN]->(Genre)<-[:WORKS_IN]-(other)-[:CREATED]->(related)`, las consultas serían más complejas y lentas. Almacenar `genre_name` como propiedad en `Artwork` permite un filtro directo:

```cypher
MATCH (related:Artwork {genre_name: aw.genre_name})
```

Esto es un **trade-off**: se duplica el dato (ya existe en `Genre.name`) a cambio de queries más simples y eficientes.

### ¿Por qué 4 tipos de nodo y no menos?

El modelo refleja fielmente las entidades del dominio:
- **Buyer** y **Artwork** son los extremos de la relación de compra.
- **Artist** es el creador de las obras y el pivote para encontrar artistas similares.
- **Genre** permite agrupar artistas por disciplina.

Separarlos en 4 nodos evita mezclar responsabilidades y permite que cada consulta navegue la red con precisión.

### ¿Por qué MERGE en lugar de CREATE en la migración?

`MERGE` evita duplicados si el script se ejecuta múltiples veces. La migración es **idempotente**: se puede ejecutar varias veces y el grafo siempre tendrá los mismos nodos y relaciones, sin duplicación.

### ¿Por qué no se eliminaron los nodos de prueba (seed) antes de migrar?

El seed y la migración usan rangos de IDs distintos (seed: 1-6; MySQL: números más altos). Esto permite que ambos conjuntos coexistan para fines de prueba. En producción se migraría desde MySQL únicamente.

### ¿Por qué las vistas están protegidas con `user_passes_test`?

Las consultas de recomendación revelan información sobre compradores y sus hábitos de compra. Solo el personal autorizado (staff/employee) debe acceder a estos reportes.

---

## 12. Limitaciones y trabajo futuro

1. **Sincronización automática (Sprint 4):** Actualmente la migración es manual. En el Sprint 4 se puede conectar vía señales Django para que cada nueva venta cree automáticamente su relación `BOUGHT` en Neo4j, o mediante un management command (`python manage.py sync_neo4j`).

2. **Recomendaciones más avanzadas con APOC:** El plugin APOC está instalado en el contenedor pero no se utiliza. Se pueden implementar algoritmos de caminos más cortos, PageRank para obras populares, o detección de comunidades de compradores.

3. **Red de compradores:** Se podría añadir una relación `:COMPRA_SIMILAR` entre compradores que adquieren las mismas obras (colaboración), permitiendo recomendar "otros compradores con gustos similares también compraron...".

4. **Constraints de unicidad para evitar migraciones duplicadas:** Los constraints UNIQUE ya están implementados, pero si se migra con datos nuevos y un mismo id relacional, se actualiza el nodo en lugar de crear uno nuevo.

5. **Integración con el flujo de ventas:** Idealmente, cuando un empleado finaliza una venta en Django, debería dispararse una señal que cree la relación `(:Buyer)-[:BOUGHT]->(:Artwork)` en Neo4j en tiempo real.
