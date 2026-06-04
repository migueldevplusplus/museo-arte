"""
db_cassandra.py — Conexión al cluster Apache Cassandra
Sprint 2: Históricos, Auditoría y Reportes

Uso:
    from cassandra_service.db_cassandra import get_session

    session = get_session()
    rows = session.execute("SELECT * FROM museo.ventas_por_mes WHERE year=2025 AND month=6")

Nota: Python 3.12+ eliminó el módulo asyncore, por lo que se debe establecer
      AsyncioConnection ANTES de importar cassandra.cluster.
"""

import os
import sys
from dotenv import load_dotenv

from cassandra.cluster import Cluster
from cassandra.policies import RoundRobinPolicy

# Cargar variables de entorno desde .env en la raíz del proyecto
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)

# ── Configuración ──────────────────────────────────────────────────────────
CASSANDRA_HOST = os.getenv('CASSANDRA_HOST', '127.0.0.1')
CASSANDRA_PORT = int(os.getenv('CASSANDRA_PORT', '9042'))
CASSANDRA_KEYSPACE = os.getenv('CASSANDRA_KEYSPACE', 'museo')

# ── Conexión (singleton) ──────────────────────────────────────────────────
_cluster = None
_session = None


def _create_cluster(**kwargs):
    """
    Crea un Cluster usando AsyncioConnection para compatibilidad con Python 3.12+.
    """
    return Cluster(
        contact_points=[CASSANDRA_HOST],
        port=CASSANDRA_PORT,
        load_balancing_policy=RoundRobinPolicy(),
        **kwargs,
    )


def get_session(keyspace=None):
    """
    Retorna una sesión Cassandra conectada al keyspace indicado.
    Si keyspace es None, usa CASSANDRA_KEYSPACE del .env.
    La conexión se reutiliza (patrón singleton).
    """
    global _cluster, _session

    if _session is not None and not _session.is_shutdown:
        return _session

    try:
        ks = keyspace or CASSANDRA_KEYSPACE

        _cluster = _create_cluster()
        _session = _cluster.connect()

        # Intentar usar el keyspace (puede no existir aún si se llama antes de crear esquema)
        try:
            _session.set_keyspace(ks)
        except Exception:
            pass  # El keyspace se creará con crear_esquema.py

        print(f"✓ Conectado a Cassandra en {CASSANDRA_HOST}:{CASSANDRA_PORT}")
        return _session

    except Exception as e:
        print(f"✗ Error conectando a Cassandra: {e}", file=sys.stderr)
        print(f"  ¿Está corriendo Cassandra? Ejecuta:", file=sys.stderr)
        print(f"  docker compose -f docker-compose.cassandra.yml up -d", file=sys.stderr)
        sys.exit(1)


def get_session_without_keyspace():
    """
    Retorna una sesión sin keyspace (para crear el keyspace inicial).
    """
    cluster = _create_cluster()
    session = cluster.connect()
    print(f"✓ Conectado a Cassandra en {CASSANDRA_HOST}:{CASSANDRA_PORT} (sin keyspace)")
    return session, cluster


def close():
    """Cierra la conexión al cluster."""
    global _cluster, _session
    if _session:
        _session.shutdown()
    if _cluster:
        _cluster.shutdown()
    _session = None
    _cluster = None
    print("✓ Conexión a Cassandra cerrada")
