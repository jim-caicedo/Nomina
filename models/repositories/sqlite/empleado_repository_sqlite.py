"""
Implementación SQLite del repositorio de empleados.
Solo persistencia. Sin lógica de negocio.
"""
from __future__ import annotations
from typing import List, Optional
import sqlite3
from database.db_manager import DBManager
from models.repositories.interfaces.empleado_repository import EmpleadoRepository
from models.domain.empleado import Empleado


class EmpleadoRepositorySQLite(EmpleadoRepository):
    """Implementación SQLite - solo persistencia"""
    
    def __init__(self, db_manager: DBManager = None):
        """Inicializa el repositorio con la conexión a BD."""
        self.db = db_manager or DBManager()

    def _row_to_empleado(self, row) -> Empleado:
        """Convierte fila SQLite a objeto Empleado"""
        recibe_aux = True
        if "recibe_auxilio_transporte" in row.keys():
            recibe_aux = bool(row["recibe_auxilio_transporte"])

        return Empleado(
            id=row["id"],
            nombre=row["nombre"],
            apellido=row["apellido"],
            cargo=row["cargo"],
            salario=float(row["salario"]),
            correo=row["correo"] or "",
            telefono=row["telefono"] or "",
            numero_cuenta=row["numero_cuenta"] or "",
            eps=row["eps"] or "EPS por asignar",
            afp=row["afp"] or "AFP por asignar",
            sede_laboral=row["sede_laboral"] or "",
            auxilio_transporte_mensual=float(row["auxilio_transporte_mensual"] or 0.0),
            fecha_ingreso=row["fecha_ingreso"],
            horas_extra=float(row["horas_extra"] or 0.0),
            recibe_auxilio_transporte=recibe_aux,
            activo=bool(row["activo"]) if "activo" in row.keys() else True,
        )
    
    def crear(self, empleado: Empleado) -> Empleado:
        """Solo persiste, NO valida reglas de negocio"""
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("""
                INSERT INTO empleados 
                (nombre, apellido, cargo, salario, correo, telefono, numero_cuenta, 
                 eps, afp, sede_laboral, auxilio_transporte_mensual, recibe_auxilio_transporte)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                empleado.nombre,
                empleado.apellido,
                empleado.cargo,
                empleado.salario,
                empleado.correo,
                empleado.telefono,
                empleado.numero_cuenta,
                empleado.eps,
                empleado.afp,
                empleado.sede_laboral,
                empleado.auxilio_transporte_mensual,
                1 if empleado.recibe_auxilio_transporte else 0,
            ))
            self.db.get_connection().commit()
            empleado.id = cursor.lastrowid
            return empleado
        except sqlite3.Error as e:
            self.db.get_connection().rollback()
            raise
    
    def obtener_por_id(self, empleado_id: int) -> Optional[Empleado]:
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("SELECT * FROM empleados WHERE id = ? AND activo = 1", (empleado_id,))
            row = cursor.fetchone()
            return self._row_to_empleado(row) if row else None
        except sqlite3.Error:
            return None
    
    def obtener_todos(self) -> List[Empleado]:
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("SELECT * FROM empleados WHERE activo = 1 ORDER BY id")
            rows = cursor.fetchall()
            return [self._row_to_empleado(row) for row in rows]
        except sqlite3.Error:
            return []
    
    def actualizar(self, empleado: Empleado) -> bool:
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("""
                UPDATE empleados
                SET nombre=?, apellido=?, cargo=?, salario=?, correo=?,
                    telefono=?, numero_cuenta=?, eps=?, afp=?, sede_laboral=?,
                    auxilio_transporte_mensual=?, recibe_auxilio_transporte=?
                WHERE id=? AND activo = 1
            """, (
                empleado.nombre,
                empleado.apellido,
                empleado.cargo,
                empleado.salario,
                empleado.correo,
                empleado.telefono,
                empleado.numero_cuenta,
                empleado.eps,
                empleado.afp,
                empleado.sede_laboral,
                empleado.auxilio_transporte_mensual,
                1 if empleado.recibe_auxilio_transporte else 0,
                empleado.id,
            ))
            self.db.get_connection().commit()
            return cursor.rowcount > 0
        except sqlite3.Error:
            return False
    
    def eliminar(self, empleado_id: int) -> bool:
        """Soft delete - marca como inactivo"""
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("UPDATE empleados SET activo = 0 WHERE id = ?", (empleado_id,))
            self.db.get_connection().commit()
            return cursor.rowcount > 0
        except sqlite3.Error:
            return False
    
    def existe(self, empleado_id: int) -> bool:
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("SELECT COUNT(*) FROM empleados WHERE id = ? AND activo = 1", (empleado_id,))
            count = cursor.fetchone()[0]
            return count > 0
        except sqlite3.Error:
            return False
