"""
Implementación SQLite del repositorio de conceptos.
Solo persistencia. Sin lógica de negocio.
"""
from __future__ import annotations
from typing import List, Optional
import sqlite3
from database.db_manager import DBManager
from models.domain.concepto import ConceptoNomina, ConceptoEmpleado, RegistroConceptoNomina


class ConceptoRepositorySQLite:
    """Implementación SQLite para catálogo de conceptos"""
    
    def __init__(self, db_manager: DBManager = None):
        self.db = db_manager or DBManager()

    def _row_to_model(self, row) -> ConceptoNomina:
        keys = row.keys() if hasattr(row, 'keys') else []

        def safe_get(column, default=None):
            try:
                if column in keys:
                    val = row[column]
                    return default if val is None else val
                return row[column] if column in row else default
            except Exception:
                return default

        return ConceptoNomina(
            id=safe_get("id", None),
            nombre=safe_get("nombre", ""),
            tipo=safe_get("tipo", "fijo"),
            naturaleza=safe_get("naturaleza", "devengado"),
            valor=safe_get("valor", None),
            porcentaje=safe_get("porcentaje", None),
            base_calculo=safe_get("base_calculo", None),
            activo=bool(safe_get("activo", 1)),
        )

    def crear(self, concepto: ConceptoNomina) -> ConceptoNomina:
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute(
                """
                INSERT INTO conceptos_nomina (nombre, tipo, naturaleza, valor, porcentaje, base_calculo, activo)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    concepto.nombre,
                    concepto.tipo,
                    concepto.naturaleza,
                    concepto.valor,
                    concepto.porcentaje,
                    concepto.base_calculo,
                    1 if concepto.activo else 0,
                ),
            )
            self.db.get_connection().commit()
            concepto.id = cursor.lastrowid
            return concepto
        except sqlite3.Error as e:
            self.db.get_connection().rollback()
            raise

    def obtener_por_id(self, concepto_id: int) -> Optional[ConceptoNomina]:
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("SELECT * FROM conceptos_nomina WHERE id = ? AND activo = 1", (concepto_id,))
            row = cursor.fetchone()
            return self._row_to_model(row) if row else None
        except sqlite3.Error:
            return None

    def obtener_todos(self) -> List[ConceptoNomina]:
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("SELECT * FROM conceptos_nomina WHERE activo = 1 ORDER BY id")
            rows = cursor.fetchall()
            return [self._row_to_model(r) for r in rows]
        except sqlite3.Error:
            return []

    def actualizar(self, concepto: ConceptoNomina) -> bool:
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute(
                """
                UPDATE conceptos_nomina
                SET nombre=?, tipo=?, naturaleza=?, valor=?, porcentaje=?, base_calculo=?, activo=?
                WHERE id=?
                """,
                (
                    concepto.nombre,
                    concepto.tipo,
                    concepto.naturaleza,
                    concepto.valor,
                    concepto.porcentaje,
                    concepto.base_calculo,
                    1 if concepto.activo else 0,
                    concepto.id,
                ),
            )
            self.db.get_connection().commit()
            return cursor.rowcount > 0
        except sqlite3.Error:
            return False

    def eliminar(self, concepto_id: int) -> bool:
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("UPDATE conceptos_nomina SET activo = 0 WHERE id = ?", (concepto_id,))
            self.db.get_connection().commit()
            return cursor.rowcount > 0
        except sqlite3.Error:
            return False


class ConceptoEmpleadoRepositorySQLite:
    """Implementación SQLite para asignaciones de conceptos a empleados"""
    
    def __init__(self, db_manager: DBManager = None):
        self.db = db_manager or DBManager()

    def _row_to_model(self, row) -> ConceptoEmpleado:
        keys = row.keys() if hasattr(row, 'keys') else []

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
            empleado_id=safe_get("empleado_id", 0),
            concepto_id=safe_get("concepto_id", None),
            nombre=safe_get("nombre", ""),
            tipo=safe_get("tipo", "fijo"),
            naturaleza=safe_get("naturaleza", "devengado"),
            valor_personalizado=safe_get("valor_personalizado", None),
            porcentaje_personalizado=safe_get("porcentaje_personalizado", None),
            base_calculo=safe_get("base_calculo", None),
            activo=bool(safe_get("activo", 1)),
        )

    def asignar(self, asignacion: ConceptoEmpleado) -> ConceptoEmpleado:
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute(
                """
                INSERT INTO conceptos_empleado 
                (empleado_id, concepto_id, nombre, tipo, naturaleza, valor_personalizado, porcentaje_personalizado, base_calculo, activo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    asignacion.empleado_id,
                    asignacion.concepto_id,
                    asignacion.nombre,
                    asignacion.tipo,
                    asignacion.naturaleza,
                    asignacion.valor_personalizado,
                    asignacion.porcentaje_personalizado,
                    asignacion.base_calculo,
                    1 if asignacion.activo else 0,
                ),
            )
            self.db.get_connection().commit()
            asignacion.id = cursor.lastrowid
            return asignacion
        except sqlite3.Error as e:
            self.db.get_connection().rollback()
            raise

    def obtener_por_empleado(self, empleado_id: int) -> List[ConceptoEmpleado]:
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("SELECT * FROM conceptos_empleado WHERE empleado_id = ? AND activo = 1", (empleado_id,))
            rows = cursor.fetchall()
            return [self._row_to_model(r) for r in rows]
        except sqlite3.Error:
            return []

    def obtener_por_id(self, asignacion_id: int) -> Optional[ConceptoEmpleado]:
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("SELECT * FROM conceptos_empleado WHERE id = ?", (asignacion_id,))
            row = cursor.fetchone()
            return self._row_to_model(row) if row else None
        except sqlite3.Error:
            return None

    def desasignar(self, asignacion_id: int) -> bool:
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("UPDATE conceptos_empleado SET activo = 0 WHERE id = ?", (asignacion_id,))
            self.db.get_connection().commit()
            return cursor.rowcount > 0
        except sqlite3.Error:
            return False


class RegistroConceptoRepositorySQLite:
    """Implementación SQLite para registros de conceptos calculados"""
    
    def __init__(self, db_manager: DBManager = None):
        self.db = db_manager or DBManager()

    def _row_to_model(self, row) -> RegistroConceptoNomina:
        keys = row.keys() if hasattr(row, 'keys') else []

        def safe_get(column, default=None):
            try:
                if column in keys:
                    val = row[column]
                    return default if val is None else val
                return row[column] if column in row else default
            except Exception:
                return default

        return RegistroConceptoNomina(
            id=safe_get("id", None),
            registro_nomina_id=safe_get("registro_nomina_id", 0),
            concepto_id=safe_get("concepto_id", None),
            concepto_nombre=safe_get("concepto_nombre", ""),
            tipo=safe_get("tipo", ""),
            naturaleza=safe_get("naturaleza", "devengado").strip().lower(),
            valor_calculado=safe_get("valor_calculado", 0.0),
            metadata=safe_get("metadata", None),
        )

    def crear(self, registro: RegistroConceptoNomina) -> RegistroConceptoNomina:
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute(
                """
                INSERT INTO registro_conceptos_nomina 
                (registro_nomina_id, concepto_nombre, tipo, naturaleza, valor_calculado, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    registro.registro_nomina_id,
                    registro.concepto_nombre,
                    registro.tipo,
                    registro.naturaleza,
                    registro.valor_calculado,
                    registro.metadata,
                ),
            )
            self.db.get_connection().commit()
            registro.id = cursor.lastrowid
            return registro
        except sqlite3.Error as e:
            self.db.get_connection().rollback()
            raise

    def obtener_por_nomina(self, registro_nomina_id: int) -> List[RegistroConceptoNomina]:
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("SELECT * FROM registro_conceptos_nomina WHERE registro_nomina_id = ?", (registro_nomina_id,))
            rows = cursor.fetchall()
            return [self._row_to_model(r) for r in rows]
        except sqlite3.Error:
            return []