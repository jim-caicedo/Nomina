"""
Repositorio para `conceptos_empleado` (asignaciones personalizadas por empleado).
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from database.db_manager import DBManager
from models.conceptos.concepto_models import ConceptoEmpleado


class ConceptoEmpleadoRepositoryBase(ABC):
    @abstractmethod
    def asignar(self, concepto_emp: ConceptoEmpleado) -> ConceptoEmpleado:
        pass

    @abstractmethod
    def obtener_por_id(self, asignacion_id: int) -> Optional[ConceptoEmpleado]:
        pass

    @abstractmethod
    def obtener_por_empleado(self, empleado_id: int) -> List[ConceptoEmpleado]:
        pass

    @abstractmethod
    def actualizar(self, concepto_emp: ConceptoEmpleado) -> bool:
        pass

    @abstractmethod
    def desasignar(self, asignacion_id: int) -> bool:
        pass


class ConceptoEmpleadoRepositorySQLite(ConceptoEmpleadoRepositoryBase):
    def __init__(self):
        self.db = DBManager()

    def _row_to_model(self, row) -> ConceptoEmpleado:
        try:
            keys = row.keys() if hasattr(row, 'keys') else []
        except Exception:
            keys = []

        def safe_get(column, default=None):
            try:
                if column in keys:
                    val = row[column]
                    return default if val is None else val
                return row[column] if column in row else default
            except Exception:
                return default

        return ConceptoEmpleado(
            id=safe_get("id", None),
            empleado_id=safe_get("empleado_id", None),
            concepto_id=safe_get("concepto_id", None),
            nombre=safe_get("nombre", ""),
            tipo=safe_get("tipo", "fijo"),
            naturaleza=safe_get("naturaleza", "devengado"),
            valor_personalizado=safe_get("valor_personalizado", None),
            porcentaje_personalizado=safe_get("porcentaje_personalizado", None),
            base_calculo=safe_get("base_calculo", None),
            activo=bool(safe_get("activo", 1)),
            fecha_asignacion=safe_get("fecha_asignacion", None),
        )

    def asignar(self, concepto_emp: ConceptoEmpleado) -> ConceptoEmpleado:
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute(
                """
                INSERT INTO conceptos_empleado (empleado_id, concepto_id, nombre, tipo, naturaleza, valor_personalizado, porcentaje_personalizado, base_calculo, activo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    concepto_emp.empleado_id,
                    concepto_emp.concepto_id,
                    concepto_emp.nombre,
                    concepto_emp.tipo,
                    concepto_emp.naturaleza,
                    concepto_emp.valor_personalizado,
                    concepto_emp.porcentaje_personalizado,
                    concepto_emp.base_calculo,
                    1 if concepto_emp.activo else 0,
                ),
            )
            self.db.get_connection().commit()
            concepto_emp.id = cursor.lastrowid
            return concepto_emp
        except Exception as e:
            print(f"Error al asignar concepto a empleado: {e}")
            self.db.get_connection().rollback()
            raise

    def obtener_por_id(self, asignacion_id: int) -> Optional[ConceptoEmpleado]:
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("SELECT * FROM conceptos_empleado WHERE id = ? AND activo = 1", (asignacion_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_model(row)
            return None
        except Exception as e:
            print(f"Error al obtener asignación: {e}")
            return None

    def obtener_por_empleado(self, empleado_id: int) -> List[ConceptoEmpleado]:
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("SELECT * FROM conceptos_empleado WHERE empleado_id = ? AND activo = 1 ORDER BY id", (empleado_id,))
            rows = cursor.fetchall()
            return [self._row_to_model(r) for r in rows]
        except Exception as e:
            print(f"Error al listar asignaciones por empleado: {e}")
            return []

    def actualizar(self, concepto_emp: ConceptoEmpleado) -> bool:
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute(
                """
                UPDATE conceptos_empleado
                SET nombre=?, tipo=?, naturaleza=?, valor_personalizado=?, porcentaje_personalizado=?, base_calculo=?, activo=?
                WHERE id=?
                """,
                (
                    concepto_emp.nombre,
                    concepto_emp.tipo,
                    concepto_emp.naturaleza,
                    concepto_emp.valor_personalizado,
                    concepto_emp.porcentaje_personalizado,
                    concepto_emp.base_calculo,
                    1 if concepto_emp.activo else 0,
                    concepto_emp.id,
                ),
            )
            self.db.get_connection().commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error al actualizar asignación: {e}")
            self.db.get_connection().rollback()
            return False

    def desasignar(self, asignacion_id: int) -> bool:
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("UPDATE conceptos_empleado SET activo = 0 WHERE id = ?", (asignacion_id,))
            self.db.get_connection().commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error al desasignar concepto: {e}")
            self.db.get_connection().rollback()
            return False
