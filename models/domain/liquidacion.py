"""
Modelo de dominio para la Liquidación Final de Contrato.
"""
from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class LiquidacionFinal:
    id: Optional[int]
    empleado_id: int
    fecha_liquida: date
    fecha_retiro: date
    motivo_retiro: str
    dias_totales_trabajados: int
    
    # Bases
    salario_base: float
    promedio_variables: float  # Suma/Promedio de Horas Extras y Recargos
    auxilio_transporte: float
    base_prestaciones: float
    
    # Conceptos Calculados
    valor_cesantias: float
    valor_intereses_cesantias: float
    valor_prima: float
    valor_vacaciones: float
    valor_indemnizacion: float
    
    # Totales
    total_devengado: float
    total_deducciones: float
    neto_a_pagar: float
    
    estado: str = "PROCESADO"  # "BORRADOR", "PROCESADO", "ANULADO"