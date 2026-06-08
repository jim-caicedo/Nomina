from dataclasses import dataclass
from datetime import date
from .i_concepto_calculable import IConceptoCalculable


@dataclass
class ConceptoFijo(IConceptoCalculable):
    nombre: str
    valor: float

    def calcular(self, empleado, periodo_inicio: date, periodo_cierre: date, valor_ingresado: float = 0.0) -> float:
        return float(self.valor)
