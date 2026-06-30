"""
Repositorio de configuración legal de nómina.
Implementa persistencia en SQLite con historial de cambios.
"""

import sqlite3
from abc import ABC, abstractmethod
from typing import List, Optional
from database.db_manager import DBManager
from models.domain.configuracion import ConfiguracionNomina


class ConfiguracionRepositoryBase(ABC):
    """Interfaz abstracta para operaciones de configuración."""

    @abstractmethod
    def obtener_configuracion_actual(self) -> ConfiguracionNomina:
        """Obtiene la configuración actual vigente."""
        pass

    @abstractmethod
    def guardar_configuracion(self, config: ConfiguracionNomina) -> ConfiguracionNomina:
        """Guarda una configuración."""
        pass


class ConfiguracionRepositorySQLite(ConfiguracionRepositoryBase):
    """Implementación del repositorio usando SQLite con historial."""

    def __init__(self):
        """Inicializa el repositorio con la conexión a BD."""
        self.db = DBManager()
        self._inicializar_si_vacio()

    def _inicializar_si_vacio(self):
        """Inicializa la BD con configuración por defecto si está vacía."""
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("SELECT COUNT(*) FROM configuracion_legal")
            count = cursor.fetchone()[0]

            if count == 0:
                config_default = ConfiguracionNomina.crear_default_2026()
                self._insertar_configuracion(config_default)
        except sqlite3.Error as e:
            print(f"Error al inicializar BD: {e}")

    def _insertar_configuracion(self, config: ConfiguracionNomina) -> None:
        """Inserta una configuración en la BD sin desactivar anterior."""
        try:
            cursor = self.db.get_connection().cursor()
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
            self.db.get_connection().commit()
        except sqlite3.Error as e:
            print(f"Error al insertar configuración: {e}")
            self.db.get_connection().rollback()

    def obtener_configuracion_actual(self) -> ConfiguracionNomina:
        """
        Obtiene la configuración actual activa desde SQLite.

        Returns:
            ConfiguracionNomina actual o por defecto si no existe

        Raises:
            Exception: Si hay error al leer de la BD
        """
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute(
                """
                SELECT id, anio_vigente, salario_minimo_mensual, auxilio_transporte_mensual,
                       porcentaje_afp, porcentaje_eps, fecha_creacion, activa
                FROM configuracion_legal
                WHERE activa = 1
                ORDER BY fecha_creacion DESC
                LIMIT 1
                """
            )
            row = cursor.fetchone()

            if row:
                return ConfiguracionNomina(
                    id=row[0],
                    anio_vigente=row[1],
                    salario_minimo_mensual=float(row[2]),
                    auxilio_transporte_mensual=float(row[3]),
                    porcentaje_afp=float(row[4]),
                    porcentaje_eps=float(row[5]),
                    fecha_creacion=row[6],
                    activa=bool(row[7]),
                )
            # Retornar default si no hay configuración activa
            return ConfiguracionNomina.crear_default_2026()
        except Exception as e:
            raise Exception(f"Error al obtener configuración: {str(e)}")

    def guardar_configuracion(self, config: ConfiguracionNomina) -> ConfiguracionNomina:
        """
        Guarda una nueva configuración y desactiva la anterior.

        Args:
            config: ConfiguracionNomina a guardar

        Returns:
            ConfiguracionNomina guardada

        Raises:
            Exception: Si hay error al guardar
        """
        try:
            # Validar configuración
            es_valida, mensaje = config.validar()
            if not es_valida:
                raise ValueError(f"Configuración inválida: {mensaje}")

            cursor = self.db.get_connection().cursor()

            # Obtener configuración activa anterior
            config_anterior = self.obtener_configuracion_actual()

            # Desactivar configuración anterior
            if config_anterior and config_anterior.id:
                cursor.execute(
                    "UPDATE configuracion_legal SET activa = 0 WHERE id = ?",
                    (config_anterior.id,),
                )

            # Insertar nueva configuración
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

            # Registrar cambios en el historial
            self._registrar_cambios(config_anterior, config, cursor)

            self.db.get_connection().commit()
            return config
        except Exception as e:
            self.db.get_connection().rollback()
            raise Exception(f"Error al guardar configuración: {str(e)}")

    def _registrar_cambios(
        self,
        config_anterior: Optional[ConfiguracionNomina],
        config_nueva: ConfiguracionNomina,
        cursor: sqlite3.Cursor,
    ) -> None:
        """Registra cambios en el historial."""
        if not config_anterior:
            return

        cambios = [
            ("salario_minimo_mensual", config_anterior.salario_minimo_mensual),
            ("auxilio_transporte_mensual", config_anterior.auxilio_transporte_mensual),
            ("porcentaje_afp", config_anterior.porcentaje_afp),
            ("porcentaje_eps", config_anterior.porcentaje_eps),
        ]

        valores_nuevos = [
            config_nueva.salario_minimo_mensual,
            config_nueva.auxilio_transporte_mensual,
            config_nueva.porcentaje_afp,
            config_nueva.porcentaje_eps,
        ]

        for (campo, valor_anterior), valor_nuevo in zip(cambios, valores_nuevos):
            if valor_anterior != valor_nuevo:
                cursor.execute(
                    """
                    INSERT INTO historial_cambios
                    (campo_cambiado, valor_anterior, valor_nuevo, usuario)
                    VALUES (?, ?, ?, 'admin')
                    """,
                    (campo, str(valor_anterior), str(valor_nuevo)),
                )

    def obtener_historial(self) -> List[ConfiguracionNomina]:
        """
        Obtiene el historial completo de configuraciones.

        Returns:
            Lista de ConfiguracionNomina ordenadas por fecha (más reciente primero)
        """
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute(
                """
                SELECT id, anio_vigente, salario_minimo_mensual, auxilio_transporte_mensual,
                       porcentaje_afp, porcentaje_eps, fecha_creacion, activa
                FROM configuracion_legal
                ORDER BY fecha_creacion DESC
                """
            )
            rows = cursor.fetchall()

            configuraciones = []
            for row in rows:
                config = ConfiguracionNomina(
                    id=row[0],
                    anio_vigente=row[1],
                    salario_minimo_mensual=float(row[2]),
                    auxilio_transporte_mensual=float(row[3]),
                    porcentaje_afp=float(row[4]),
                    porcentaje_eps=float(row[5]),
                    fecha_creacion=row[6],
                    activa=bool(row[7]),
                )
                configuraciones.append(config)

            return configuraciones
        except sqlite3.Error as e:
            print(f"Error al obtener historial: {e}")
            return []

    def obtener_historial_cambios(self) -> List[dict]:
        """Obtiene el historial de cambios de configuración."""
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute(
                """
                SELECT id, campo_cambiado, valor_anterior, valor_nuevo, fecha_cambio, usuario
                FROM historial_cambios
                ORDER BY fecha_cambio DESC
                """
            )
            rows = cursor.fetchall()

            cambios = []
            for row in rows:
                cambios.append(
                    {
                        "id": row[0],
                        "campo_cambiado": row[1],
                        "valor_anterior": row[2],
                        "valor_nuevo": row[3],
                        "fecha_cambio": row[4],
                        "usuario": row[5],
                    }
                )
            return cambios
        except sqlite3.Error as e:
            print(f"Error al obtener historial de cambios: {e}")
            return []
