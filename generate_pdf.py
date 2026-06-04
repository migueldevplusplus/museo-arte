import os
import sys
from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        # Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Título
        self.cell(0, 10, 'Resumen Ejecutivo: Sprint 2 (Apache Cassandra)', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, 'Proyecto Academico: Plataforma Poliglota para el Museo de Arte', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 8, title, 0, 1, 'L', 1)
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 6, body)
        self.ln(4)


def create_pdf():
    pdf = PDF()
    pdf.add_page()
    
    # 1. Objetivo General
    pdf.chapter_title('1. Objetivo del Sprint 2')
    pdf.chapter_body(
        "Se diseno e implemento un microservicio de base de datos NoSQL utilizando Apache Cassandra "
        "para gestionar la alta disponibilidad de datos historicos del museo. El objetivo principal "
        "fue resolver dos necesidades gerenciales criticas: generar resumenes masivos de facturacion "
        "y mantener una bitacora inmutable de auditoria de seguridad."
    )
    
    # 2. Infraestructura
    pdf.chapter_title('2. Despliegue de Infraestructura')
    pdf.chapter_body(
        "Se configuro un entorno local con Docker (docker-compose.cassandra.yml) para levantar "
        "un nodo de Apache Cassandra, permitiendo el desarrollo sin afectar el core transaccional MySQL. "
        "Se instalaron y configuraron los drivers de Python compatibles (cassandra-driver) adaptandolos "
        "a las restricciones de Python 3.12+."
    )
    
    # 3. Diseno de Datos
    pdf.chapter_title('3. Diseno del Modelo de Datos (Query-Driven Modeling)')
    pdf.chapter_body(
        "Se aplico el paradigma de Query-Driven Modeling propio de Cassandra, desnormalizando "
        "la informacion en 5 familias de columnas, cada una optimizada para consultas (O(1)): \n\n"
        "- ventas_por_mes: Facturacion mensual.\n"
        "- ventas_por_artista: Acumulados de ventas por artista.\n"
        "- ventas_por_genero: Acumulados de ventas por genero artistico.\n"
        "- bitacora_eventos: Registro inmutable de acciones en el sistema.\n"
        "- historial_estatus_obra: Trazabilidad de transiciones (AVAILABLE -> RESERVED -> SOLD)."
    )
    
    # 4. Procesamiento ETL
    pdf.chapter_title('4. Proceso de Migracion (ETL)')
    pdf.chapter_body(
        "Se desarrollo el script 'migrar_mysql_a_cassandra.py' que extrae las ventas historicas "
        "y datos operacionales del core relacional (MySQL), los transforma al esquema desnormalizado "
        "y los carga en Cassandra. Ademas, se implemento 'seed_cassandra.py' para generar miles de "
        "registros sinteticos y probar el rendimiento."
    )

    # 5. Resultados y Consultas
    pdf.chapter_title('5. Entregables y Consultas Gerenciales')
    pdf.chapter_body(
        "Se entrego el script 'consultas_cassandra.py' con 10 reportes gerenciales operativos:\n"
        "- Resumenes de ventas con calculo de IVA y comisiones del museo.\n"
        "- Rankings de los artistas mas rentables.\n"
        "- Busquedas avanzadas en la bitacora por tipo de evento y mes.\n"
        "Todo respaldado por una base de datos optimizada para lecturas masivas y alta disponibilidad."
    )
    
    output_path = os.path.join(os.path.dirname(__file__), 'Resumen_Sprint2_Cassandra.pdf')
    pdf.output(output_path)
    print(f"PDF generado exitosamente en: {output_path}")


if __name__ == '__main__':
    create_pdf()
