from dataclasses import dataclass
from datetime import date
from .i_concepto_calculable import IConceptoCalculable


@dataclass
class ConceptoVariable(IConceptoCalculable):
    nombre: str

    def calcular(self, empleado, periodo_inicio: date, periodo_cierre: date, valor_ingresado: float = 0.0) -> float:
        try:
            return float(valor_ingresado)
        except Exception:
            return 0.0
