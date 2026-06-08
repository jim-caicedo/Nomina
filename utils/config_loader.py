"""
Utilidad para cargar y inicializar configuración de nómina.
"""

from pathlib import Path
from models.configuracion import ConfiguracionNomina
from models.configuracion_repository import ConfiguracionRepositoryJSON


def inicializar_configuracion_default(ruta_archivo: str = "data/config_nomina.json") -> ConfiguracionNomina:
    """
    Inicializa el archivo de configuración con valores por defecto de 2026 si no existe.

    Args:
        ruta_archivo: Ruta del archivo JSON de configuración

    Returns:
        ConfiguracionNomina con valores por defecto
    """
    ruta = Path(ruta_archivo)

    # Si no existe el archivo, crearlo con defaults
    if not ruta.exists():
        # Crear directorio padre si no existe
        ruta.parent.mkdir(parents=True, exist_ok=True)

        # Crear configuración por defecto
        config_default = ConfiguracionNomina.crear_default_2026()

        # Guardar usando el repositorio
        repo = ConfiguracionRepositoryJSON(ruta_archivo)
        repo.guardar_configuracion(config_default)

        return config_default

    # Si existe, cargar configuración actual
    repo = ConfiguracionRepositoryJSON(ruta_archivo)
    return repo.obtener_configuracion_actual()


def obtener_configuracion_actual(ruta_archivo: str = "data/config_nomina.json") -> ConfiguracionNomina:
    """
    Obtiene la configuración actual del sistema.

    Args:
        ruta_archivo: Ruta del archivo JSON de configuración

    Returns:
        ConfiguracionNomina actual
    """
    repo = ConfiguracionRepositoryJSON(ruta_archivo)
    return repo.obtener_configuracion_actual()
