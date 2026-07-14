"""
Implementación SQLite del repositorio de empleados.
Solo persistencia. Sin lógica de negocio.
"""
from __future__ import annotations
from typing import List, Optional
import sqlite3
from database.db_manager import DBManager
from models.domain.empleado import Empleado


class EmpleadoRepositorySQLite:
    """Implementación SQLite — solo persistencia."""

    def __init__(self, db_manager: DBManager = None):
        self.db = db_manager or DBManager()

    def _row_to_empleado(self, row) -> Empleado:
        keys = row.keys()
        return Empleado(
            id=row["id"],
            nombre=row["nombre"],
            apellido=row["apellido"],
            cargo=row["cargo"],
            salario=float(row["salario"]),
            correo=row["correo"] or "",
            telefono=row["telefono"] or "",
            numero_cuenta=row["numero_cuenta"] or "",
            eps=row["eps"] or "",
            afp=row["afp"] or "",
            sede_laboral=row["sede_laboral"] or "",
            cedula=row["cedula"] or "" if "cedula" in keys else "",
            fecha_ingreso=row["fecha_ingreso"],
            horas_extra=float(row["horas_extra"] or 0.0),
            recibe_auxilio_transporte=bool(row["recibe_auxilio_transporte"])
                if "recibe_auxilio_transporte" in keys else True,
            activo=bool(row["activo"]) if "activo" in keys else True,
            codigo_banco=row["codigo_banco"] or "" if "codigo_banco" in keys else "",
            tipo_cuenta=row["tipo_cuenta"] or "AHORROS" if "tipo_cuenta" in keys else "AHORROS",
            tipo_documento=row["tipo_documento"] or "CC" if "tipo_documento" in keys else "CC",
        )

    def crear(self, empleado: Empleado) -> Empleado:
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("""
                INSERT INTO empleados
                (nombre, apellido, cargo, salario, correo, telefono, numero_cuenta,
                 eps, afp, sede_laboral, cedula, recibe_auxilio_transporte,
                 codigo_banco, tipo_cuenta, tipo_documento)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                empleado.nombre, empleado.apellido, empleado.cargo,
                empleado.salario, empleado.correo, empleado.telefono,
                empleado.numero_cuenta, empleado.eps, empleado.afp,
                empleado.sede_laboral, empleado.cedula,
                1 if empleado.recibe_auxilio_transporte else 0,
                empleado.codigo_banco, empleado.tipo_cuenta, empleado.tipo_documento,
            ))
            self.db.get_connection().commit()
            empleado.id = cursor.lastrowid
            return empleado
        except sqlite3.Error:
            self.db.get_connection().rollback()
            raise

    def obtener_por_id(self, empleado_id: int) -> Optional[Empleado]:
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute(
                "SELECT * FROM empleados WHERE id = ? AND activo = 1", (empleado_id,)
            )
            row = cursor.fetchone()
            return self._row_to_empleado(row) if row else None
        except sqlite3.Error:
            return None

    def obtener_todos(self) -> List[Empleado]:
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("SELECT * FROM empleados WHERE activo = 1 ORDER BY id")
            return [self._row_to_empleado(r) for r in cursor.fetchall()]
        except sqlite3.Error:
            return []

    def actualizar(self, empleado: Empleado) -> bool:
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("""
                UPDATE empleados
                SET nombre=?, apellido=?, cargo=?, salario=?, correo=?,
                    telefono=?, numero_cuenta=?, eps=?, afp=?, sede_laboral=?,
                    cedula=?, recibe_auxilio_transporte=?,
                    codigo_banco=?, tipo_cuenta=?, tipo_documento=?
                WHERE id=? AND activo = 1
            """, (
                empleado.nombre, empleado.apellido, empleado.cargo,
                empleado.salario, empleado.correo, empleado.telefono,
                empleado.numero_cuenta, empleado.eps, empleado.afp,
                empleado.sede_laboral, empleado.cedula,
                1 if empleado.recibe_auxilio_transporte else 0,
                empleado.codigo_banco, empleado.tipo_cuenta, empleado.tipo_documento,
                empleado.id,
            ))
            self.db.get_connection().commit()
            return cursor.rowcount > 0
        except sqlite3.Error:
            return False

    def eliminar(self, empleado_id: int) -> bool:
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute(
                "UPDATE empleados SET activo = 0 WHERE id = ?", (empleado_id,)
            )
            self.db.get_connection().commit()
            return cursor.rowcount > 0
        except sqlite3.Error:
            return False

    def existe(self, empleado_id: int) -> bool:
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM empleados WHERE id = ? AND activo = 1", (empleado_id,)
            )
            return cursor.fetchone()[0] > 0
        except sqlite3.Error:
            return False
