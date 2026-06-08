"""
Script para inicializar la base de datos con configuración por defecto.
"""

from database.db_manager import DBManager
from models.configuracion import ConfiguracionNomina
from models.configuracion_repository import ConfiguracionRepositorySQLite
from config.constants import (
    SALARIO_MINIMO_2026,
    AUXILIO_TRANSPORTE_2026,
    PORCENTAJE_AFP,
    PORCENTAJE_EPS,
)


def seed_database():
    """Inicializa la BD con configuración por defecto para 2026."""
    # Verificar si ya hay datos
    repo = ConfiguracionRepositorySQLite()
    config_existente = repo.obtener_configuracion_activa()

    if config_existente:
        print("La base de datos ya tiene una configuración activa. Abortando seed.")
        return

    # Crear configuración por defecto para 2026
    config_2026 = ConfiguracionNomina.crear_default_2026()

    # Guardar en BD
    if repo.guardar_nueva_configuracion(config_2026):
        print("✓ Base de datos inicializada correctamente con configuración 2026")
        print(f"  - SMMLV 2026: ${config_2026.salario_minimo_mensual:,.0f}")
        print(f"  - Auxilio Transporte: ${config_2026.auxilio_transporte_mensual:,.0f}")
        print(f"  - AFP: {config_2026.porcentaje_afp * 100}%")
        print(f"  - EPS: {config_2026.porcentaje_eps * 100}%")
    else:
        print("✗ Error al inicializar la base de datos")


if __name__ == "__main__":
    seed_database()
