from dataclasses import dataclass
from datetime import date
from typing import Literal
from .i_concepto_calculable import IConceptoCalculable


BaseCalculo = Literal["salario", "ventas"]


@dataclass
class ConceptoPorcentaje(IConceptoCalculable):
    nombre: str
    porcentaje: float
    base_calculo: BaseCalculo = "salario"

    def calcular(self, empleado, periodo_inicio: date, periodo_cierre: date, valor_ingresado: float = 0.0) -> float:
        base = 0.0
        if self.base_calculo == "salario":
            base = getattr(empleado, "salario", 0.0) or 0.0
        elif self.base_calculo == "ventas":
            base = float(valor_ingresado) if valor_ingresado else 0.0

        return (base * float(self.porcentaje)) / 100.0
