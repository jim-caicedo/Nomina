"""
Modelo de dominio RegistroNomina.
Solo datos y validaciones básicas. Sin lógica de negocio ni persistencia.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import date, datetime
from typing import Dict, Optional


@dataclass
class RegistroNomina:
    """Registro de liquidación de nómina para un empleado en un período"""
    id: Optional[int] = None
    empleado_id: int = 0
    periodo_id: Optional[int] = None
    periodo_inicio: date = None
    periodo_cierre: date = None
    dias_laborados: int = 0
    salario_base_periodo: float = 0.0
    auxilio_transporte_periodo: float = 0.0
    horas_extras: int = 0
    valor_horas_extras: float = 0.0
    total_devengado: float = 0.0
    descuento_afp: float = 0.0
    descuento_eps: float = 0.0
    otros_descuentos: float = 0.0
    total_deducciones: float = 0.0
    salario_neto: float = 0.0
    fecha_liquidacion: Optional[datetime] = None
    
    def validar(self) -> tuple[bool, str]:
        """Validación básica de datos"""
        if self.empleado_id <= 0:
            return False, "ID de empleado inválido"
        if self.dias_laborados <= 0:
            return False, "Días laborados debe ser positivo"
        if self.periodo_inicio is None or self.periodo_cierre is None:
            return False, "Período debe tener fechas de inicio y cierre"
        if self.periodo_inicio > self.periodo_cierre:
            return False, "Fecha de inicio debe ser anterior a fecha de cierre"
        return True, ""
    
    def to_dict(self) -> Dict[str, object]:
        return {
            "id": self.id,
            "empleado_id": self.empleado_id,
            "periodo_id": self.periodo_id,
            "periodo_inicio": self.periodo_inicio.strftime("%Y-%m-%d") if self.periodo_inicio else None,
            "periodo_cierre": self.periodo_cierre.strftime("%Y-%m-%d") if self.periodo_cierre else None,
            "dias_laborados": self.dias_laborados,
            "salario_base_periodo": self.salario_base_periodo,
            "auxilio_transporte_periodo": self.auxilio_transporte_periodo,
            "horas_extras": self.horas_extras,
            "valor_horas_extras": self.valor_horas_extras,
            "total_devengado": self.total_devengado,
            "descuento_afp": self.descuento_afp,
            "descuento_eps": self.descuento_eps,
            "otros_descuentos": self.otros_descuentos,
            "total_deducciones": self.total_deducciones,
            "salario_neto": self.salario_neto,
            "fecha_liquidacion": self.fecha_liquidacion.strftime("%Y-%m-%d %H:%M:%S") if self.fecha_liquidacion else None,
        }
