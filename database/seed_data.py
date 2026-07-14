"""
Datos iniciales para una base de datos vacía.
Solo se usan al crear la BD por primera vez o al restaurar la configuración base.
Los valores vigentes en runtime siempre provienen de data/nomina.db.
"""

from __future__ import annotations

from typing import Dict

from database.db_manager import DBManager
from models.domain.configuracion import ConfiguracionNomina

# Valores base para la primera carga de la BD (bootstrap)
CONFIGURACION_INICIAL: Dict[str, float | int] = {
    "anio_vigente": 2026,
    "salario_minimo_mensual": 1_423_500.0,
    "auxilio_transporte_mensual": 161_916.0,
    "porcentaje_afp": 0.04,
    "porcentaje_eps": 0.04,
}


def crear_configuracion_inicial() -> ConfiguracionNomina:
    """Crea el objeto de configuración para seed o restauración."""
    return ConfiguracionNomina(
        anio_vigente=int(CONFIGURACION_INICIAL["anio_vigente"]),
        salario_minimo_mensual=float(CONFIGURACION_INICIAL["salario_minimo_mensual"]),
        auxilio_transporte_mensual=float(CONFIGURACION_INICIAL["auxilio_transporte_mensual"]),
        porcentaje_afp=float(CONFIGURACION_INICIAL["porcentaje_afp"]),
        porcentaje_eps=float(CONFIGURACION_INICIAL["porcentaje_eps"]),
        activa=True,
    )


def seed_configuracion_si_vacia(db: DBManager | None = None) -> bool:
    """
    Inserta la configuración inicial si la tabla está vacía.

    Returns:
        True si se insertó seed, False si ya existían registros.
    """
    manager = db or DBManager()
    try:
        cursor = manager.get_connection().cursor()
        cursor.execute("SELECT COUNT(*) FROM configuracion_legal")
        if cursor.fetchone()[0] > 0:
            return False

        config = crear_configuracion_inicial()
        cursor.execute(
            """
            INSERT INTO configuracion_legal
            (anio_vigente, salario_minimo_mensual, auxilio_transporte_mensual,
             porcentaje_afp, porcentaje_eps, activa)
            VALUES (?, ?, ?, ?, ?, 1)
            """,
            (
                config.anio_vigente,
                config.salario_minimo_mensual,
                config.auxilio_transporte_mensual,
                config.porcentaje_afp,
                config.porcentaje_eps,
            ),
        )
        manager.get_connection().commit()
        return True
    except Exception as e:
        print(f"Error al sembrar configuración legal: {e}")
        manager.get_connection().rollback()
        return False


def seed_database() -> None:
    """Inicializa la BD con configuración legal si no existe ninguna activa."""
    DBManager()
    seed_configuracion_si_vacia()

    from models.repositories.sqlite.configuracion_repository_sqlite import ConfiguracionRepositorySQLite

    repo = ConfiguracionRepositorySQLite()
    config = repo.obtener_configuracion_actual()

    print("✓ Verificación de configuración legal completada")
    print(f"  - Año vigente: {config.anio_vigente}")
    print(f"  - SMMLV: ${config.salario_minimo_mensual:,.0f}")
    print(f"  - Auxilio transporte: ${config.auxilio_transporte_mensual:,.0f}")
    print(f"  - AFP: {config.porcentaje_afp * 100:.0f}%")
    print(f"  - EPS: {config.porcentaje_eps * 100:.0f}%")


if __name__ == "__main__":
    seed_database()
