"""
Repositorio de registros de nómina.
Implementa el patrón Repository con persistencia en SQLite.
"""
from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional
from database.db_manager import DBManager
from models.registro_nomina import RegistroNomina


class NominaRepositoryBase(ABC):
    """Interfaz abstracta para operaciones de nómina."""

    @abstractmethod
    def guardar_registro(self, registro: RegistroNomina) -> RegistroNomina:
        """Guarda un registro de nómina."""
        pass

    @abstractmethod
    def obtener_por_periodo(
        self, fecha_inicio: date, fecha_cierre: date
    ) -> List[RegistroNomina]:
        """Obtiene todos los registros de un período."""
        pass

    @abstractmethod
    def obtener_historial_empleado(self, empleado_id: int) -> List[RegistroNomina]:
        """Obtiene el historial de nómina de un empleado."""
        pass

    @abstractmethod
    def obtener_por_id(self, registro_id: int) -> Optional[RegistroNomina]:
        """Obtiene un registro específico por ID."""
        pass


class NominaRepositorySQLite(NominaRepositoryBase):
    """Implementación del repositorio usando SQLite con persistencia real."""

    def __init__(self):
        """Inicializa el repositorio con la conexión a BD."""
        self.db = DBManager()

    def _row_to_registro(self, row) -> RegistroNomina:
        """Convierte una fila de SQLite en objeto RegistroNomina."""
        from datetime import datetime
        
        return RegistroNomina(
            id=row["id"],
            empleado_id=row["empleado_id"],
            periodo_inicio=datetime.strptime(row["periodo_inicio"], "%Y-%m-%d").date(),
            periodo_cierre=datetime.strptime(row["periodo_cierre"], "%Y-%m-%d").date(),
            dias_laborados=row["dias_laborados"],
            salario_base_periodo=float(row["salario_base_periodo"]),
            auxilio_transporte_periodo=float(row["auxilio_transporte_periodo"]),
            horas_extras=row["horas_extras"],
            valor_horas_extras=float(row["valor_horas_extras"]),
            total_devengado=float(row["total_devengado"]),
            descuento_afp=float(row["descuento_afp"]),
            descuento_eps=float(row["descuento_eps"]),
            otros_descuentos=float(row["otros_descuentos"] or 0.0),
            total_deducciones=float(row["total_deducciones"]),
            salario_neto=float(row["salario_neto"]),
            fecha_liquidacion=datetime.strptime(row["fecha_liquidacion"], "%Y-%m-%d %H:%M:%S") if row["fecha_liquidacion"] else None,
        )

    def guardar_registro(self, registro: RegistroNomina) -> RegistroNomina:
        """Guarda un nuevo registro de nómina en la BD."""
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("""
                INSERT INTO registros_nomina 
                (empleado_id, periodo_inicio, periodo_cierre, dias_laborados,
                 salario_base_periodo, auxilio_transporte_periodo, horas_extras,
                 valor_horas_extras, total_devengado, descuento_afp, descuento_eps,
                 otros_descuentos, total_deducciones, salario_neto)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                registro.empleado_id,
                registro.periodo_inicio.strftime("%Y-%m-%d"),
                registro.periodo_cierre.strftime("%Y-%m-%d"),
                registro.dias_laborados,
                registro.salario_base_periodo,
                registro.auxilio_transporte_periodo,
                registro.horas_extras,
                registro.valor_horas_extras,
                registro.total_devengado,
                registro.descuento_afp,
                registro.descuento_eps,
                registro.otros_descuentos,
                registro.total_deducciones,
                registro.salario_neto,
            ))
            self.db.get_connection().commit()
            
            # Asignar ID generado
            registro.id = cursor.lastrowid
            return registro
        except Exception as e:
            print(f"Error al guardar registro de nómina: {e}")
            self.db.get_connection().rollback()
            raise

    def obtener_por_periodo(
        self, fecha_inicio: date, fecha_cierre: date
    ) -> List[RegistroNomina]:
        """Obtiene todos los registros de un período específico."""
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("""
                SELECT * FROM registros_nomina 
                WHERE periodo_inicio = ? AND periodo_cierre = ?
                ORDER BY id
            """, (
                fecha_inicio.strftime("%Y-%m-%d"),
                fecha_cierre.strftime("%Y-%m-%d"),
            ))
            rows = cursor.fetchall()
            
            return [self._row_to_registro(row) for row in rows]
        except Exception as e:
            print(f"Error al obtener registros por período: {e}")
            return []

    def obtener_historial_empleado(self, empleado_id: int) -> List[RegistroNomina]:
        """Obtiene el historial de nómina de un empleado ordenado por fecha."""
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("""
                SELECT * FROM registros_nomina 
                WHERE empleado_id = ?
                ORDER BY periodo_cierre DESC
            """, (empleado_id,))
            rows = cursor.fetchall()
            
            return [self._row_to_registro(row) for row in rows]
        except Exception as e:
            print(f"Error al obtener historial: {e}")
            return []

    def obtener_por_id(self, registro_id: int) -> Optional[RegistroNomina]:
        """Obtiene un registro específico por ID."""
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("SELECT * FROM registros_nomina WHERE id = ?", (registro_id,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_registro(row)
            return None
        except Exception as e:
            print(f"Error al obtener registro: {e}")
            return None

    def obtener_todos(self) -> List[RegistroNomina]:
        """Obtiene todos los registros de nómina."""
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("SELECT * FROM registros_nomina ORDER BY fecha_liquidacion DESC")
            rows = cursor.fetchall()
            
            return [self._row_to_registro(row) for row in rows]
        except Exception as e:
            print(f"Error al obtener todos los registros: {e}")
            return []

    def eliminar(self, registro_id: int) -> bool:
        """Elimina un registro de nómina."""
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("DELETE FROM registros_nomina WHERE id = ?", (registro_id,))
            self.db.get_connection().commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error al eliminar registro: {e}")
            self.db.get_connection().rollback()
            return False