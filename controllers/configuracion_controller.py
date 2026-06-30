"""
Controlador de configuración legal de nómina.
Maneja la lógica de negocio para configuración de parámetros legales.
"""

from typing import Dict, List
from models.domain.configuracion import ConfiguracionNomina
from models.configuracion_repository import ConfiguracionRepositorySQLite


class ConfiguracionController:
    """Controlador para gestión de configuración legal de nómina."""

    def __init__(self):
        self.repo = ConfiguracionRepositorySQLite()

    def cargar_configuracion(self) -> Dict[str, object]:
        """
        Carga la configuración actual del sistema.

        Returns:
            Diccionario con la configuración actual
        """
        try:
            config = self.repo.obtener_configuracion_actual()
            return {
                "success": True,
                "config": {
                    "id": config.id,
                    "anio_vigente": config.anio_vigente,
                    "salario_minimo_mensual": config.salario_minimo_mensual,
                    "auxilio_transporte_mensual": config.auxilio_transporte_mensual,
                    "porcentaje_afp": config.porcentaje_afp,
                    "porcentaje_eps": config.porcentaje_eps,
                    "fecha_creacion": config.fecha_creacion,
                    "activa": config.activa,
                },
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error al cargar configuración: {str(e)}",
            }

    def guardar_configuracion(
        self,
        anio: int,
        salario_minimo: float,
        auxilio_transporte: float,
        porcentaje_afp: float,
        porcentaje_eps: float,
    ) -> Dict[str, object]:
        """
        Guarda una nueva configuración legal en SQLite.

        Args:
            anio: Año vigente (ej: 2026)
            salario_minimo: Salario mínimo mensual
            auxilio_transporte: Auxilio de transporte mensual
            porcentaje_afp: Porcentaje AFP (ej: 0.04 para 4%)
            porcentaje_eps: Porcentaje EPS (ej: 0.04 para 4%)

        Returns:
            Diccionario con resultado de la operación
        """
        try:
            # Validaciones de entrada
            if not (2020 <= anio <= 2050):
                return {
                    "success": False,
                    "error": "El año debe estar entre 2020 y 2050.",
                }

            if salario_minimo <= 0:
                return {
                    "success": False,
                    "error": "El salario mínimo debe ser positivo.",
                }

            if auxilio_transporte < 0:
                return {
                    "success": False,
                    "error": "El auxilio de transporte no puede ser negativo.",
                }

            # Convertir porcentajes de formato 4.0 a 0.04 si el usuario ingresa 4 en lugar de 0.04
            if porcentaje_afp > 1:
                porcentaje_afp = porcentaje_afp / 100

            if porcentaje_eps > 1:
                porcentaje_eps = porcentaje_eps / 100

            if not (0 <= porcentaje_afp <= 1):
                return {
                    "success": False,
                    "error": "El porcentaje AFP debe estar entre 0 y 100 (o 0 y 1).",
                }

            if not (0 <= porcentaje_eps <= 1):
                return {
                    "success": False,
                    "error": "El porcentaje EPS debe estar entre 0 y 100 (o 0 y 1).",
                }

            # Crear objeto de configuración
            config = ConfiguracionNomina(
                id=None,  # SQLite asigna ID automático
                anio_vigente=anio,
                salario_minimo_mensual=salario_minimo,
                auxilio_transporte_mensual=auxilio_transporte,
                porcentaje_afp=porcentaje_afp,
                porcentaje_eps=porcentaje_eps,
                fecha_creacion=None,  # SQLite asigna CURRENT_TIMESTAMP
                activa=True,
            )

            # Guardar en repositorio
            config_guardada = self.repo.guardar_configuracion(config)

            return {
                "success": True,
                "mensaje": "Configuración guardada exitosamente.",
                "config": {
                    "id": config_guardada.id,
                    "anio_vigente": config_guardada.anio_vigente,
                    "salario_minimo_mensual": config_guardada.salario_minimo_mensual,
                    "auxilio_transporte_mensual": config_guardada.auxilio_transporte_mensual,
                    "porcentaje_afp": config_guardada.porcentaje_afp,
                    "porcentaje_eps": config_guardada.porcentaje_eps,
                },
            }

        except ValueError as e:
            return {
                "success": False,
                "error": str(e),
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error al guardar configuración: {str(e)}",
            }

    def restaurar_defaults_2026(self) -> Dict[str, object]:
        """
        Restaura los valores por defecto de 2026 en la BD.

        Returns:
            Diccionario con resultado de la operación
        """
        try:
            config_default = ConfiguracionNomina.crear_default_2026()
            config_guardada = self.repo.guardar_configuracion(config_default)

            return {
                "success": True,
                "mensaje": "Configuración restaurada a valores por defecto de 2026.",
                "config": {
                    "id": config_guardada.id,
                    "anio_vigente": config_guardada.anio_vigente,
                    "salario_minimo_mensual": config_guardada.salario_minimo_mensual,
                    "auxilio_transporte_mensual": config_guardada.auxilio_transporte_mensual,
                    "porcentaje_afp": config_guardada.porcentaje_afp,
                    "porcentaje_eps": config_guardada.porcentaje_eps,
                },
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error al restaurar configuración: {str(e)}",
            }

    def obtener_configuracion_obj(self) -> ConfiguracionNomina:
        """
        Obtiene el objeto ConfiguracionNomina actual.

        Returns:
            Objeto ConfiguracionNomina actual
        """
        return self.repo.obtener_configuracion_actual()

    def obtener_historial_configuraciones(self) -> List[Dict[str, object]]:
        """
        Obtiene el historial de todas las configuraciones guardadas.

        Returns:
            Lista de configuraciones con sus detalles
        """
        configuraciones = self.repo.obtener_historial()
        return [
            {
                "id": c.id,
                "anio_vigente": c.anio_vigente,
                "salario_minimo_mensual": c.salario_minimo_mensual,
                "auxilio_transporte_mensual": c.auxilio_transporte_mensual,
                "porcentaje_afp": c.porcentaje_afp,
                "porcentaje_eps": c.porcentaje_eps,
                "fecha_creacion": c.fecha_creacion,
                "activa": c.activa,
            }
            for c in configuraciones
        ]

    def obtener_historial_cambios(self) -> List[Dict[str, object]]:
        """
        Obtiene el historial detallado de cambios de configuración.

        Returns:
            Lista de cambios registrados
        """
        return self.repo.obtener_historial_cambios()
