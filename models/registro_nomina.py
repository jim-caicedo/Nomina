"""
Modelo RegistroNomina para almacenar cálculos de nómina de un período.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Dict, Optional


@dataclass
class RegistroNomina:
    """
    Registro completo de liquidación de nómina para un empleado en un período.
    Almacena todos los valores devengados, deducciones y el resultado final.
    """

    id: int
    empleado_id: int
    periodo_inicio: date
    periodo_cierre: date
    dias_laborados: int

    # DEVENGADOS
    salario_base_periodo: float  # Ordinario del período
    auxilio_transporte_periodo: float
    horas_extras: int
    valor_horas_extras: float
    total_devengado: float

    # DEDUCCIONES
    descuento_afp: float
    descuento_eps: float
    total_deducciones: float

    # RESULTADO
    salario_neto: float
    otros_descuentos: float = 0.0
    fecha_liquidacion: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, object]:
        """Convierte el registro a diccionario."""
        return {
            "id": self.id,
            "empleado_id": self.empleado_id,
            "periodo_inicio": self.periodo_inicio.strftime("%d/%m/%Y"),
            "periodo_cierre": self.periodo_cierre.strftime("%d/%m/%Y"),
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
            "fecha_liquidacion": self.fecha_liquidacion.strftime("%d/%m/%Y %H:%M:%S"),
        }
