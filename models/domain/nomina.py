"""
Modelos de dominio para nómina.
RegistroNomina: resultado persistido de una liquidación.
ResultadoLiquidacion: resultado en memoria de un cálculo (no se persiste directamente).
ItemConcepto: ítem de concepto dentro de un resultado de liquidación.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Dict, List, Optional


@dataclass
class ItemConcepto:
    """Un concepto aplicado dentro de un resultado de liquidación"""
    nombre: str
    tipo: str
    naturaleza: str     # devengado | deduccion
    valor: float


@dataclass
class ResultadoLiquidacion:
    """
    Resultado en memoria de calcular la nómina de un empleado.
    No se persiste — el controlador lo convierte a RegistroNomina para guardarlo.
    """
    ordinario: float
    auxilio_transporte: float
    horas_extras: float
    total_devengado: float
    salario_base_periodo: float
    descuento_afp: float
    descuento_eps: float
    otros_descuentos: float
    total_deducciones: float
    salario_neto: float
    conceptos_aplicados: List[ItemConcepto] = field(default_factory=list)
    conceptos_omitidos: List[Dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "ordinario": self.ordinario,
            "auxilio_transporte": self.auxilio_transporte,
            "horas_extras": self.horas_extras,
            "total_devengado": self.total_devengado,
            "salario_base_periodo": self.salario_base_periodo,
            "descuento_afp": self.descuento_afp,
            "descuento_eps": self.descuento_eps,
            "otros_descuentos": self.otros_descuentos,
            "total_deducciones": self.total_deducciones,
            "salario_neto": self.salario_neto,
            "conceptos_aplicados": [
                {
                    "nombre": c.nombre,
                    "tipo": c.tipo,
                    "naturaleza": c.naturaleza,
                    "valor": c.valor,
                }
                for c in self.conceptos_aplicados
            ],
            "conceptos_omitidos": self.conceptos_omitidos,
        }


@dataclass
class RegistroNomina:
    """
    Registro persistido de la liquidación de un empleado en un período.
    Es lo que se guarda en la tabla `registros_nomina`.

    Nota: la tabla física NO tiene columna `periodo_id`. El período se
    identifica mediante `periodo_inicio` + `periodo_cierre`.
    """
    id: int
    empleado_id: int
    periodo_inicio: date
    periodo_cierre: date
    dias_laborados: int
    salario_base_periodo: float
    auxilio_transporte_periodo: float
    horas_extras: int
    valor_horas_extras: float
    total_devengado: float
    descuento_afp: float
    descuento_eps: float
    otros_descuentos: float
    total_deducciones: float
    salario_neto: float
    fecha_liquidacion: Optional[datetime] = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, object]:
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
            "fecha_liquidacion": (
                self.fecha_liquidacion.strftime("%d/%m/%Y %H:%M:%S")
                if self.fecha_liquidacion else ""
            ),
        }