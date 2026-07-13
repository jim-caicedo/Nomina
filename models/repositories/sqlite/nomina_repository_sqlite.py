"""
Implementación SQLite del repositorio de nómina.
Solo persistencia. Sin lógica de negocio.
"""
from __future__ import annotations
from typing import List, Optional
from datetime import date, datetime
import sqlite3
from database.db_manager import DBManager
from models.repositories.interfaces.nomina_repository import NominaRepository
from models.domain.nomina import RegistroNomina


class NominaRepositorySQLite(NominaRepository):
    """Implementación SQLite - solo persistencia"""
    
    def __init__(self, db_manager: DBManager = None):
        """Inicializa el repositorio con la conexión a BD."""
        self.db = db_manager or DBManager()

    def _row_to_registro(self, row) -> RegistroNomina:
        """Convierte fila SQLite a objeto RegistroNomina"""
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
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("""
                INSERT INTO registros_nomina 
                (empleado_id, periodo_id, periodo_inicio, periodo_cierre, dias_laborados,
                 salario_base_periodo, auxilio_transporte_periodo, horas_extras,
                 valor_horas_extras, total_devengado, descuento_afp, descuento_eps,
                 otros_descuentos, total_deducciones, salario_neto)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                registro.empleado_id,
                registro.periodo_id,
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
        except sqlite3.Error as e:
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

    def obtener_por_periodo_id(self, periodo_id: int) -> List[RegistroNomina]:
        """¡NUEVO MÉTODO! Reemplaza la búsqueda por fechas primitivas y busca por ID real"""
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("""
                SELECT * FROM registros_nomina 
                WHERE periodo_id = ?
                ORDER BY id
            """, (periodo_id,))
            rows = cursor.fetchall()
            return [self._row_to_registro(row) for row in rows]
        except sqlite3.Error:
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
    
    def obtener_por_periodo(self, fecha_inicio: date, fecha_cierre: date) -> List[RegistroNomina]:
            """
            Método exigido por la interfaz base abstracta.
            Para mantener compatibilidad y que no estalle el sistema, busca 
            los registros usando un JOIN con la tabla periodos_nomina.
            """
            try:
                cursor = self.db.get_connection().cursor()
                cursor.execute("""
                    SELECT r.* FROM registros_nomina r
                    JOIN periodos_nomina p ON r.periodo_id = p.id
                    WHERE p.fecha_inicio = ? AND p.fecha_fin = ?
                    ORDER BY r.id
                """, (
                    fecha_inicio.strftime("%Y-%m-%d") if isinstance(fecha_inicio, date) else fecha_inicio,
                    fecha_cierre.strftime("%Y-%m-%d") if isinstance(fecha_cierre, date) else fecha_cierre,
                ))
                rows = cursor.fetchall()
                return [self._row_to_registro(row) for row in rows]
            except sqlite3.Error as e:
                print(f"Error en obtener_por_periodo (legacy): {e}")
                return []
