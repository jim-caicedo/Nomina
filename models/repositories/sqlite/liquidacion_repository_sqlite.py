"""
Repositorio SQLite para la persistencia de Liquidaciones Finales de Contrato.
"""
import sqlite3
from datetime import date, datetime
from typing import List, Optional
from models.domain.liquidacion import LiquidacionFinal

class LiquidacionRepositorySQLite:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._crear_tabla()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _crear_tabla(self) -> None:
        """Crea la tabla de liquidaciones si no existe."""
        query = """
        CREATE TABLE IF NOT EXISTS liquidaciones_finales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empleado_id INTEGER NOT NULL,
            fecha_liquida TEXT NOT NULL,
            fecha_retiro TEXT NOT NULL,
            motivo_retiro TEXT NOT NULL,
            dias_totales_trabajados INTEGER NOT NULL,
            salario_base REAL NOT NULL,
            promedio_variables REAL NOT NULL,
            auxilio_transporte REAL NOT NULL,
            base_prestaciones REAL NOT NULL,
            valor_cesantias REAL NOT NULL,
            valor_intereses_cesantias REAL NOT NULL,
            valor_prima REAL NOT NULL,
            valor_vacaciones REAL NOT NULL,
            valor_indemnizacion REAL NOT NULL,
            total_devengado REAL NOT NULL,
            total_deducciones REAL NOT NULL,
            neto_a_pagar REAL NOT NULL,
            estado TEXT NOT NULL DEFAULT 'PROCESADO',
            FOREIGN KEY (empleado_id) REFERENCES empleados (id)
        );
        """
        with self._get_connection() as conn:
            conn.execute(query)

    def obtener_sumatoria_horas_extras_y_variables(
        self, 
        empleado_id: int, 
        fecha_inicio: date, 
        fecha_fin: date
    ) -> float:
        """
        Consulta las horas extras y devengados adicionales pagados en nóminas 
        cerradas entre fecha_inicio y fecha_fin para promediar en la base prestacional.
        """
        # Consulta sumando valores devengados de horas extras / recargos
        # Ajusta las columnas 'registros_nomina' o 'conceptos_nomina' según tu esquema de BD
        query = """
        SELECT COALESCE(SUM(rn.valor_horas_extras), 0.0) as total_he
        FROM registros_nomina rn
        WHERE rn.empleado_id = ?
          AND rn.fecha_inicio >= ?
          AND rn.fecha_cierre <= ?
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                query, 
                (empleado_id, fecha_inicio.isoformat(), fecha_fin.isoformat())
            )
            row = cursor.fetchone()
            return float(row["total_he"]) if row else 0.0

    def guardar(self, liq: LiquidacionFinal) -> LiquidacionFinal:
        """Guarda la liquidación final e inactiva al empleado en la misma transacción."""
        query_liq = """
        INSERT INTO liquidaciones_finales (
            empleado_id, fecha_liquida, fecha_retiro, motivo_retiro,
            dias_totales_trabajados, salario_base, promedio_variables,
            auxilio_transporte, base_prestaciones, valor_cesantias,
            valor_intereses_cesantias, valor_prima, valor_vacaciones,
            valor_indemnizacion, total_devengado, total_deducciones,
            neto_a_pagar, estado
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        query_empleado = """
        UPDATE empleados SET estado = 'INACTIVO' WHERE id = ?
        """

        with self._get_connection() as conn:
            cursor = conn.execute(query_liq, (
                liq.empleado_id,
                liq.fecha_liquida.isoformat() if isinstance(liq.fecha_liquida, date) else liq.fecha_liquida,
                liq.fecha_retiro.isoformat() if isinstance(liq.fecha_retiro, date) else liq.fecha_retiro,
                liq.motivo_retiro,
                liq.dias_totales_trabajados,
                liq.salario_base,
                liq.promedio_variables,
                liq.auxilio_transporte,
                liq.base_prestaciones,
                liq.valor_cesantias,
                liq.valor_intereses_cesantias,
                liq.valor_prima,
                liq.valor_vacaciones,
                liq.valor_indemnizacion,
                liq.total_devengado,
                liq.total_deducciones,
                liq.neto_a_pagar,
                liq.estado
            ))
            liq.id = cursor.lastrowid
            
            # Cambiamos estado del empleado
            conn.execute(query_empleado, (liq.empleado_id,))
            conn.commit()
            
        return liq