"""
Implementación SQLite del repositorio de nómina.
Solo persistencia. Sin lógica de negocio.
"""
from __future__ import annotations
from typing import List, Optional
from datetime import date, datetime
import sqlite3
from database.db_manager import DBManager
from models.domain.nomina import RegistroNomina


class NominaRepositorySQLite:
    """Implementación SQLite - solo persistencia"""

    def __init__(self, db_manager: DBManager = None):
        """Inicializa el repositorio con la conexión a BD."""
        self.db = db_manager or DBManager()

    def _row_to_registro(self, row) -> RegistroNomina:
        """Convierte fila SQLite a objeto RegistroNomina."""
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
            fecha_liquidacion=(
                datetime.strptime(row["fecha_liquidacion"], "%Y-%m-%d %H:%M:%S")
                if row["fecha_liquidacion"] else None
            ),
        )

    def guardar_registro(self, registro: RegistroNomina) -> RegistroNomina:
        """INSERT en registros_nomina. La tabla física NO tiene periodo_id."""
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("""
                INSERT INTO registros_nomina
                (empleado_id, periodo_inicio, periodo_cierre, dias_laborados,
                 salario_base_periodo, auxilio_transporte_periodo, horas_extras,
                 valor_horas_extras, total_devengado, descuento_afp, descuento_eps,
                 otros_descuentos, total_deducciones, salario_neto, fecha_liquidacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now','localtime'))
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
            registro.id = cursor.lastrowid
            return registro
        except sqlite3.Error:
            self.db.get_connection().rollback()
            raise

    def obtener_por_id(self, registro_id: int) -> Optional[RegistroNomina]:
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("SELECT * FROM registros_nomina WHERE id = ?", (registro_id,))
            row = cursor.fetchone()
            return self._row_to_registro(row) if row else None
        except sqlite3.Error:
            return None

    def obtener_todos(self) -> List[RegistroNomina]:
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("SELECT * FROM registros_nomina ORDER BY fecha_liquidacion DESC")
            rows = cursor.fetchall()
            return [self._row_to_registro(row) for row in rows]
        except sqlite3.Error:
            return []

    def obtener_por_periodo(self, fecha_inicio: date, fecha_cierre: date) -> List[RegistroNomina]:
        """
        Devuelve todos los registros de nómina pertenecientes a un período
        identificado por su rango de fechas (no hay tabla periodos_nomina).
        """
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("""
                SELECT * FROM registros_nomina
                WHERE periodo_inicio = ? AND periodo_cierre = ?
                ORDER BY id
            """, (
                fecha_inicio.strftime("%Y-%m-%d") if isinstance(fecha_inicio, date) else fecha_inicio,
                fecha_cierre.strftime("%Y-%m-%d") if isinstance(fecha_cierre, date) else fecha_cierre,
            ))
            rows = cursor.fetchall()
            return [self._row_to_registro(row) for row in rows]
        except sqlite3.Error as e:
            print(f"Error en obtener_por_periodo: {e}")
            return []

    def obtener_por_empleado(self, empleado_id: int) -> List[RegistroNomina]:
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("""
                SELECT * FROM registros_nomina
                WHERE empleado_id = ?
                ORDER BY periodo_cierre DESC
            """, (empleado_id,))
            rows = cursor.fetchall()
            return [self._row_to_registro(row) for row in rows]
        except sqlite3.Error:
            return []

    def periodo_esta_cerrado(self, fecha_inicio: date, fecha_cierre: date) -> bool:
        """
        True si ya existe al menos una liquidación para ese rango.
        Reemplaza la columna `estado` de la inexistente tabla periodos_nomina.
        """
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM registros_nomina
                WHERE periodo_inicio = ? AND periodo_cierre = ?
            """, (
                fecha_inicio.strftime("%Y-%m-%d") if isinstance(fecha_inicio, date) else fecha_inicio,
                fecha_cierre.strftime("%Y-%m-%d") if isinstance(fecha_cierre, date) else fecha_cierre,
            ))
            return cursor.fetchone()[0] > 0
        except sqlite3.Error:
            return False

    def existe_liquidacion_empleado(self, empleado_id: int, fecha_inicio: date, fecha_cierre: date) -> bool:
        """True si un empleado ya tiene liquidación en el período indicado."""
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM registros_nomina
                WHERE empleado_id = ? AND periodo_inicio = ? AND periodo_cierre = ?
            """, (
                empleado_id,
                fecha_inicio.strftime("%Y-%m-%d") if isinstance(fecha_inicio, date) else fecha_inicio,
                fecha_cierre.strftime("%Y-%m-%d") if isinstance(fecha_cierre, date) else fecha_cierre,
            ))
            return cursor.fetchone()[0] > 0
        except sqlite3.Error:
            return False