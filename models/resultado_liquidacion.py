from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ItemConcepto:
    nombre: str
    tipo: str
    naturaleza: str
    valor: float


@dataclass
class ResultadoLiquidacion:
    # Devengados base
    ordinario: float
    auxilio_transporte: float
    horas_extras: float
    total_devengado: float

    # Base de cálculo para deducciones
    salario_base_periodo: float

    # Deducciones obligatorias
    descuento_afp: float
    descuento_eps: float
    otros_descuentos: float
    total_deducciones: float

    # Resultado final
    salario_neto: float

    # Conceptos variables aplicados
    conceptos_aplicados: List[ItemConcepto]
    conceptos_omitidos: List[Dict[str, str]]

    def to_dict(self) -> dict:
        """Convierte a diccionario para compatibilidad con código existente."""
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
