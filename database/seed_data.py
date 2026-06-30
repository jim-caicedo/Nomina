"""
Script para inicializar la base de datos con configuración por defecto.
"""

from database.db_manager import DBManager
from models.domain.configuracion import ConfiguracionNomina
from models.configuracion_repository import ConfiguracionRepositorySQLite


def seed_database():
    """Inicializa la BD con configuración por defecto para 2026."""
    repo = ConfiguracionRepositorySQLite()
    config_existente = repo.obtener_configuracion_actual()

    if config_existente.id is not None:
        print("La base de datos ya tiene una configuración activa. Abortando seed.")
        return

    config_2026 = ConfiguracionNomina.crear_default_2026()

    try:
        repo.guardar_configuracion(config_2026)
        print("✓ Base de datos inicializada correctamente con configuración 2026")
        print(f"  - SMMLV 2026: ${config_2026.salario_minimo_mensual:,.0f}")
        print(f"  - Auxilio Transporte: ${config_2026.auxilio_transporte_mensual:,.0f}")
        print(f"  - AFP: {config_2026.porcentaje_afp * 100}%")
        print(f"  - EPS: {config_2026.porcentaje_eps * 100}%")
    except Exception as e:
        print(f"✗ Error al inicializar la base de datos: {e}")


if __name__ == "__main__":
    seed_database()
