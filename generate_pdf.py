"""
Genera el PDF entregable del Sprint 2 — Modelo de Familias de Columnas
y Scripts CQL para Consultas Gerenciales.
"""

import os
from fpdf import FPDF, XPos, YPos


class EntregablePDF(FPDF):

    # ── Encabezado / Pie ────────────────────────────────────────────────
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, "Sprint 2 - Museo de Arte Contemporaneo", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
        self.set_draw_color(41, 128, 185)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Pagina {self.page_no()}/{{nb}}", align="C")

    # ── Helpers ─────────────────────────────────────────────────────────
    def titulo_principal(self, txt):
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(41, 128, 185)
        self.cell(0, 12, txt, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        self.ln(2)

    def subtitulo(self, txt):
        self.set_font("Helvetica", "I", 11)
        self.set_text_color(80, 80, 80)
        self.cell(0, 8, txt, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        self.ln(6)

    def seccion(self, num, txt):
        self.ln(4)
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(41, 128, 185)
        self.cell(0, 8, f"{num}. {txt}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(41, 128, 185)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def subseccion(self, txt):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(50, 50, 50)
        self.cell(0, 7, txt, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)

    def parrafo(self, txt):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 5.5, txt)
        self.ln(3)

    def codigo(self, txt):
        self.set_font("Courier", "", 8.5)
        self.set_fill_color(240, 240, 240)
        self.set_text_color(30, 30, 30)
        # Recuadro con padding
        x0 = self.get_x()
        y0 = self.get_y()
        self.multi_cell(0, 4.5, txt, fill=True)
        self.ln(3)

    def tabla_header(self, cols, widths):
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(41, 128, 185)
        self.set_text_color(255, 255, 255)
        for c, w in zip(cols, widths):
            self.cell(w, 7, c, border=1, fill=True, align="C")
        self.ln()

    def tabla_row(self, cols, widths, fill=False):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(30, 30, 30)
        if fill:
            self.set_fill_color(235, 245, 255)
        for c, w in zip(cols, widths):
            self.cell(w, 6, c, border=1, fill=fill, align="L")
        self.ln()

    def nota(self, txt):
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(100, 100, 100)
        self.multi_cell(0, 5, txt)
        self.ln(2)

    def tabla_key(self, label, value):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(41, 128, 185)
        self.cell(45, 6, label)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(30, 30, 30)
        self.cell(0, 6, value, new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def build_pdf():
    pdf = EntregablePDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)

    # ════════════════════════════════════════════════════════════════════
    # PORTADA
    # ════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.ln(30)
    pdf.titulo_principal("Entregable Sprint 2")
    pdf.titulo_principal("Apache Cassandra")
    pdf.ln(6)
    pdf.subtitulo("Modelo de Familias de Columnas y Scripts CQL")
    pdf.subtitulo("para Tablas Especializadas y Consultas Gerenciales")
    pdf.ln(15)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(50, 50, 50)
    info = [
        ("Proyecto:", "Plataforma Poliglota - Museo de Arte Contemporaneo"),
        ("Curso:", "Sistemas de Bases de Datos II"),
        ("Motor:", "Apache Cassandra 4.1 (Docker)"),
        ("Paradigma:", "Query-Driven Modeling (Familias de Columnas)"),
    ]
    for label, value in info:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(35, 8, label)
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 8, value, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(20)
    pdf.set_draw_color(41, 128, 185)
    pdf.set_line_width(1)
    pdf.line(50, pdf.get_y(), 160, pdf.get_y())

    # ════════════════════════════════════════════════════════════════════
    # 1. OBJETIVO
    # ════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.seccion(1, "Objetivo del Sprint")
    pdf.parrafo(
        "Disenar familias de columnas basadas estrictamente en las consultas del administrador "
        "del museo, definiendo correctamente las Partition Keys y Clustering Columns para "
        "garantizar lecturas O(1) y un modelo que siga el principio de Query-Driven Modeling."
    )
    pdf.parrafo(
        "El entregable incluye: el modelo de 5 familias de columnas con justificacion "
        "de cada Partition Key y Clustering Column, los scripts CQL de creacion (DDL), "
        "y las 10 consultas gerenciales que demuestran como cada tabla responde a una "
        "pregunta de negocio concreta."
    )

    # ════════════════════════════════════════════════════════════════════
    # 2. PRINCIPIO DE DISENO
    # ════════════════════════════════════════════════════════════════════
    pdf.seccion(2, "Principio de Diseno: Query-Driven Modeling")
    pdf.parrafo(
        "En Apache Cassandra, el modelo de datos se disena a partir de las consultas "
        "que necesita el administrador, NO a partir de las entidades (como en el modelo "
        "relacional). Esto implica:"
    )
    pdf.parrafo(
        "1) Se identifica cada pregunta del negocio.\n"
        "2) Se crea UNA tabla dedicada a responder esa pregunta.\n"
        "3) Se eligen Partition Key y Clustering Columns de forma que la consulta "
        "solo necesite acceder a UNA particion (lectura O(1)).\n"
        "4) Se DESNORMALIZAN datos (se duplican entre tablas) para evitar JOINs, "
        "que Cassandra no soporta."
    )
    pdf.nota(
        "Trade-off aceptado: se usa mas espacio en disco a cambio de lecturas "
        "extremadamente rapidas y alta disponibilidad."
    )

    # ════════════════════════════════════════════════════════════════════
    # 3. KEYSPACE
    # ════════════════════════════════════════════════════════════════════
    pdf.seccion(3, "Definicion del Keyspace")
    pdf.codigo(
        "CREATE KEYSPACE IF NOT EXISTS museo\n"
        "WITH replication = {\n"
        "    'class': 'SimpleStrategy',\n"
        "    'replication_factor': 1\n"
        "};"
    )
    pdf.parrafo(
        "Se utiliza SimpleStrategy con factor de replicacion 1 para el entorno "
        "de desarrollo local (un unico nodo Docker). En un ambiente de produccion "
        "se utilizaria NetworkTopologyStrategy con RF=3 para garantizar tolerancia "
        "a fallos."
    )

    # ════════════════════════════════════════════════════════════════════
    # 4. FAMILIAS DE COLUMNAS (TABLAS)
    # ════════════════════════════════════════════════════════════════════
    pdf.seccion(4, "Modelo de Familias de Columnas")
    pdf.parrafo(
        "Se disenaron 5 familias de columnas. A continuacion se presenta cada una "
        "con su consulta asociada, justificacion de la Partition Key (PK) y las "
        "Clustering Columns (CC), y el script CQL de creacion."
    )

    # ── TABLA 1 ─────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.subseccion("4.1  Tabla: ventas_por_mes")
    pdf.ln(2)
    pdf.tabla_key("Consulta que responde:", "Cuanto se facturo en el mes X del ano Y?")
    pdf.tabla_key("Partition Key:", "(year, month)")
    pdf.tabla_key("Clustering Columns:", "sale_date DESC, sale_id DESC")
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 6, "Justificacion de la PK y CC:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.parrafo(
        "- La PK compuesta (year, month) agrupa todas las ventas de un mismo mes en una "
        "sola particion, permitiendo obtener el resumen mensual en una sola lectura.\n"
        "- sale_date DESC como primera CC ordena las ventas cronologicamente (mas recientes primero).\n"
        "- sale_id DESC como segunda CC desambigua ventas que ocurren en el mismo instante, "
        "evitando colisiones de clave."
    )

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Script CQL:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)
    pdf.codigo(
        "CREATE TABLE IF NOT EXISTS ventas_por_mes (\n"
        "    year             INT,\n"
        "    month            INT,\n"
        "    sale_date        TIMESTAMP,\n"
        "    sale_id          INT,\n"
        "    artwork_id       INT,\n"
        "    artwork_title    TEXT,\n"
        "    artist_name      TEXT,\n"
        "    genre_name       TEXT,\n"
        "    buyer_username   TEXT,\n"
        "    payment_method   TEXT,\n"
        "    subtotal         DECIMAL,\n"
        "    iva              DECIMAL,\n"
        "    commission       DECIMAL,\n"
        "    total            DECIMAL,\n"
        "    PRIMARY KEY ((year, month), sale_date, sale_id)\n"
        ") WITH CLUSTERING ORDER BY (sale_date DESC, sale_id DESC);"
    )

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Ejemplo de consulta CQL:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)
    pdf.codigo("SELECT * FROM ventas_por_mes WHERE year = 2025 AND month = 6;")

    # ── TABLA 2 ─────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.subseccion("4.2  Tabla: ventas_por_artista")
    pdf.ln(2)
    pdf.tabla_key("Consulta que responde:", "Cuales son las ventas del artista X?")
    pdf.tabla_key("Partition Key:", "(artist_name)")
    pdf.tabla_key("Clustering Columns:", "sale_date DESC, sale_id DESC")
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Justificacion de la PK y CC:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.parrafo(
        "- La PK (artist_name) agrupa todas las ventas de un artista en una sola particion. "
        "Esto permite calcular la facturacion total, comisiones y ranking de un artista "
        "con una unica lectura.\n"
        "- sale_date DESC ordena cronologicamente y sale_id desambigua."
    )

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Script CQL:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)
    pdf.codigo(
        "CREATE TABLE IF NOT EXISTS ventas_por_artista (\n"
        "    artist_name      TEXT,\n"
        "    sale_date        TIMESTAMP,\n"
        "    sale_id          INT,\n"
        "    artwork_id       INT,\n"
        "    artwork_title    TEXT,\n"
        "    genre_name       TEXT,\n"
        "    buyer_username   TEXT,\n"
        "    payment_method   TEXT,\n"
        "    subtotal         DECIMAL,\n"
        "    iva              DECIMAL,\n"
        "    commission       DECIMAL,\n"
        "    total            DECIMAL,\n"
        "    PRIMARY KEY ((artist_name), sale_date, sale_id)\n"
        ") WITH CLUSTERING ORDER BY (sale_date DESC, sale_id DESC);"
    )

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Ejemplo de consulta CQL:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)
    pdf.codigo("SELECT * FROM ventas_por_artista WHERE artist_name = 'Pablo Picasso';")

    # ── TABLA 3 ─────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.subseccion("4.3  Tabla: ventas_por_genero")
    pdf.ln(2)
    pdf.tabla_key("Consulta que responde:", "Cuales son las ventas del genero artistico X?")
    pdf.tabla_key("Partition Key:", "(genre_name)")
    pdf.tabla_key("Clustering Columns:", "sale_date DESC, sale_id DESC")
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Justificacion de la PK y CC:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.parrafo(
        "- La PK (genre_name) agrupa ventas por tipo de arte, permitiendo analisis "
        "de tendencias del mercado artistico con una sola lectura.\n"
        "- Es una tabla separada de ventas_por_artista porque Cassandra no soporta "
        "consultas eficientes por columnas que no sean parte de la PK. Duplicar datos "
        "es el patron correcto."
    )

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Script CQL:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)
    pdf.codigo(
        "CREATE TABLE IF NOT EXISTS ventas_por_genero (\n"
        "    genre_name       TEXT,\n"
        "    sale_date        TIMESTAMP,\n"
        "    sale_id          INT,\n"
        "    artwork_id       INT,\n"
        "    artwork_title    TEXT,\n"
        "    artist_name      TEXT,\n"
        "    buyer_username   TEXT,\n"
        "    payment_method   TEXT,\n"
        "    subtotal         DECIMAL,\n"
        "    iva              DECIMAL,\n"
        "    commission       DECIMAL,\n"
        "    total            DECIMAL,\n"
        "    PRIMARY KEY ((genre_name), sale_date, sale_id)\n"
        ") WITH CLUSTERING ORDER BY (sale_date DESC, sale_id DESC);"
    )

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Ejemplo de consulta CQL:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)
    pdf.codigo("SELECT * FROM ventas_por_genero WHERE genre_name = 'Pintura';")

    pdf.nota(
        "Justificacion de 3 tablas de ventas: Cassandra no soporta JOINs ni indices "
        "secundarios eficientes. Tener ventas_por_mes, ventas_por_artista y ventas_por_genero "
        "es el patron correcto: se duplican datos para que cada consulta sea O(1). "
        "El trade-off en espacio es aceptable dado el volumen manejable de un museo."
    )

    # ── TABLA 4 ─────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.subseccion("4.4  Tabla: bitacora_eventos (Auditoria)")
    pdf.ln(2)
    pdf.tabla_key("Consulta que responde:", "Que eventos de tipo X ocurrieron en el mes Y?")
    pdf.tabla_key("Partition Key:", "(event_year, event_month, event_type)")
    pdf.tabla_key("Clustering Columns:", "event_timestamp DESC, event_id DESC")
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Justificacion de la PK y CC:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.parrafo(
        "- La PK compuesta (event_year, event_month, event_type) evita particiones "
        "que crezcan infinitamente. Si solo se usara event_type, la particion 'VENTA' "
        "creceria sin limite. Al agregar year+month, cada particion esta ACOTADA "
        "(bounded partition) al numero de eventos de un tipo en un mes.\n"
        "- event_id es UUID para evitar colisiones cuando dos eventos ocurren en el "
        "mismo timestamp exacto (patron estandar para logs en Cassandra).\n"
        "- Esta tabla es INMUTABLE: solo INSERT, nunca UPDATE ni DELETE."
    )

    pdf.parrafo(
        "Tipos de evento soportados: VENTA, RESERVA, CANCELACION, CAMBIO_ESTATUS, "
        "REGISTRO_USUARIO, MEMBRESIA."
    )

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Script CQL:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)
    pdf.codigo(
        "CREATE TABLE IF NOT EXISTS bitacora_eventos (\n"
        "    event_year       INT,\n"
        "    event_month      INT,\n"
        "    event_type       TEXT,\n"
        "    event_timestamp  TIMESTAMP,\n"
        "    event_id         UUID,\n"
        "    user_username    TEXT,\n"
        "    description      TEXT,\n"
        "    entity_type      TEXT,\n"
        "    entity_id        TEXT,\n"
        "    old_value        TEXT,\n"
        "    new_value        TEXT,\n"
        "    PRIMARY KEY ((event_year, event_month, event_type),\n"
        "                 event_timestamp, event_id)\n"
        ") WITH CLUSTERING ORDER BY\n"
        "    (event_timestamp DESC, event_id DESC);"
    )

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Ejemplo de consulta CQL:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)
    pdf.codigo(
        "SELECT * FROM bitacora_eventos\n"
        "WHERE event_year = 2025\n"
        "  AND event_month = 3\n"
        "  AND event_type = 'VENTA';"
    )

    # ── TABLA 5 ─────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.subseccion("4.5  Tabla: historial_estatus_obra")
    pdf.ln(2)
    pdf.tabla_key("Consulta que responde:", "Cual es el historial de cambios de la obra X?")
    pdf.tabla_key("Partition Key:", "(artwork_id)")
    pdf.tabla_key("Clustering Columns:", "change_timestamp DESC")
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Justificacion de la PK y CC:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.parrafo(
        "- La PK (artwork_id) agrupa todo el historial de una obra en una sola particion. "
        "Cada obra tiene un numero limitado de cambios de estatus (tipicamente 2-4: "
        "AVAILABLE -> RESERVED -> SOLD), asi que la particion esta naturalmente acotada.\n"
        "- change_timestamp DESC muestra los cambios mas recientes primero.\n"
        "- Se desnormalizan artwork_title y changed_by para evitar consultas adicionales."
    )

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Script CQL:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)
    pdf.codigo(
        "CREATE TABLE IF NOT EXISTS historial_estatus_obra (\n"
        "    artwork_id       INT,\n"
        "    change_timestamp TIMESTAMP,\n"
        "    artwork_title    TEXT,\n"
        "    old_status       TEXT,\n"
        "    new_status       TEXT,\n"
        "    changed_by       TEXT,\n"
        "    reason           TEXT,\n"
        "    PRIMARY KEY ((artwork_id), change_timestamp)\n"
        ") WITH CLUSTERING ORDER BY (change_timestamp DESC);"
    )

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Ejemplo de consulta CQL:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)
    pdf.codigo("SELECT * FROM historial_estatus_obra WHERE artwork_id = 1;")

    # ════════════════════════════════════════════════════════════════════
    # 5. RESUMEN DE PARTITION KEYS Y CLUSTERING COLUMNS
    # ════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.seccion(5, "Resumen de Partition Keys y Clustering Columns")

    widths = [42, 50, 42, 56]
    pdf.tabla_header(["Tabla", "Partition Key", "Clustering", "Consulta"], widths)
    rows_data = [
        ("ventas_por_mes", "(year, month)", "sale_date, sale_id", "Facturacion mensual"),
        ("ventas_por_artista", "(artist_name)", "sale_date, sale_id", "Ventas por artista"),
        ("ventas_por_genero", "(genre_name)", "sale_date, sale_id", "Ventas por genero"),
        ("bitacora_eventos", "(year, month, type)", "timestamp, event_id", "Auditoria por tipo/mes"),
        ("historial_estatus", "(artwork_id)", "change_timestamp", "Historial de obra"),
    ]
    for i, row in enumerate(rows_data):
        pdf.tabla_row(row, widths, fill=(i % 2 == 0))

    pdf.ln(6)
    pdf.parrafo(
        "Todas las tablas utilizan CLUSTERING ORDER BY ... DESC para que los datos "
        "mas recientes aparezcan primero, evitando ORDER BY en tiempo de consulta "
        "(que Cassandra solo permite en el orden del clustering definido en la tabla)."
    )

    # ════════════════════════════════════════════════════════════════════
    # 6. CONSULTAS GERENCIALES IMPLEMENTADAS
    # ════════════════════════════════════════════════════════════════════
    pdf.seccion(6, "Consultas Gerenciales Implementadas")
    pdf.parrafo(
        "Se implementaron 10 consultas gerenciales divididas en dos bloques: "
        "facturacion y auditoria. Cada consulta aprovecha el modelo Query-Driven "
        "para resolver la pregunta de negocio en una sola lectura por particion."
    )

    pdf.subseccion("Bloque 1: Facturacion")
    q_fact = [
        ("Q1", "ventas_por_mes", "Facturacion de un mes especifico",
         "SELECT * FROM ventas_por_mes\nWHERE year = ? AND month = ?;"),
        ("Q2", "ventas_por_mes", "Facturacion de un periodo (rango de meses)",
         "-- Iteracion mes a mes en Python\nSELECT subtotal, iva, commission, total\nFROM ventas_por_mes\nWHERE year = ? AND month = ?;"),
        ("Q3", "ventas_por_artista", "Ventas de un artista especifico",
         "SELECT * FROM ventas_por_artista\nWHERE artist_name = ?;"),
        ("Q4", "ventas_por_genero", "Ventas de un genero especifico",
         "SELECT * FROM ventas_por_genero\nWHERE genre_name = ?;"),
        ("Q5", "ventas_por_artista", "Ranking de artistas por facturacion",
         "SELECT total, commission\nFROM ventas_por_artista\nWHERE artist_name = ?;\n-- Iteracion por artista, ordenar en Python"),
        ("Q6", "ventas_por_genero", "Ranking de generos por facturacion",
         "SELECT total FROM ventas_por_genero\nWHERE genre_name = ?;\n-- Iteracion por genero, ordenar en Python"),
    ]
    for qid, tabla, desc, cql in q_fact:
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, f"{qid}: {desc}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, f"Tabla: {tabla}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_text_color(30, 30, 30)
        pdf.codigo(cql)

    pdf.add_page()
    pdf.subseccion("Bloque 2: Auditoria y Bitacora")
    q_audit = [
        ("Q7", "bitacora_eventos", "Eventos por tipo en un mes",
         "SELECT * FROM bitacora_eventos\nWHERE event_year = ?\n  AND event_month = ?\n  AND event_type = ?;"),
        ("Q8", "bitacora_eventos", "Resumen de todos los eventos del mes",
         "-- Iteracion por cada event_type:\nSELECT event_timestamp, user_username, description\nFROM bitacora_eventos\nWHERE event_year = ?\n  AND event_month = ?\n  AND event_type = ?;"),
        ("Q9", "historial_estatus_obra", "Historial de estatus de una obra",
         "SELECT * FROM historial_estatus_obra\nWHERE artwork_id = ?;"),
        ("Q10", "ventas_por_mes", "Listado de obras vendidas en periodo",
         "SELECT sale_id, sale_date, artwork_title,\n       artist_name, genre_name,\n       buyer_username, total\nFROM ventas_por_mes\nWHERE year = ? AND month = ?;\n-- Iteracion mes a mes del rango"),
    ]
    for qid, tabla, desc, cql in q_audit:
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, f"{qid}: {desc}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, f"Tabla: {tabla}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_text_color(30, 30, 30)
        pdf.codigo(cql)

    # ════════════════════════════════════════════════════════════════════
    # 7. JUSTIFICACION DE DECISIONES
    # ════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.seccion(7, "Justificacion de Decisiones de Diseno")

    pdf.subseccion("Por que 3 tablas de ventas en vez de 1?")
    pdf.parrafo(
        "Cassandra no soporta JOINs ni indices secundarios eficientes. Tener "
        "ventas_por_mes, ventas_por_artista y ventas_por_genero es el patron correcto "
        "en Cassandra: se duplican datos para que cada consulta sea O(1) por partition key. "
        "El trade-off (espacio extra) es aceptable dado que las ventas de un museo son un "
        "volumen manejable."
    )

    pdf.subseccion("Por que la bitacora tiene (year, month, type) como PK?")
    pdf.parrafo(
        "Si usaramos solo event_type, la particion de 'VENTA' creceria infinitamente. "
        "Al agregar year + month, cada particion esta ACOTADA (bounded partition) al "
        "numero de eventos de un tipo en un mes. Este es un patron recomendado para "
        "time-series en Cassandra."
    )

    pdf.subseccion("Por que UUID en event_id?")
    pdf.parrafo(
        "Evita colisiones cuando dos eventos ocurren en el mismo timestamp exacto. "
        "Es el patron estandar para logs en Cassandra."
    )

    pdf.subseccion("Por que Clustering Order DESC?")
    pdf.parrafo(
        "Los administradores siempre quieren ver primero lo mas reciente. DESC evita "
        "un ORDER BY en la consulta, que Cassandra ejecuta eficientemente SOLO en el "
        "orden del clustering definido en la tabla."
    )

    pdf.subseccion("Coexistencia MySQL <-> Cassandra")
    pdf.parrafo(
        "MySQL (core relacional) es el origen de verdad transaccional (ACID). "
        "Cassandra es el almacen de lectura optimizado para reportes gerenciales. "
        "MySQL maneja consistencia fuerte; Cassandra ofrece consistencia eventual "
        "(aceptable para reportes historicos). Los datos fluyen de MySQL a Cassandra "
        "via el script ETL de migracion."
    )

    # ── Guardar ─────────────────────────────────────────────────────────
    out = os.path.join(os.path.dirname(__file__),
                       "Entregable_Sprint2_Cassandra.pdf")
    pdf.output(out)
    print(f"PDF generado: {out}")


if __name__ == "__main__":
    build_pdf()
