from typing import Dict

class Nomina:
    IVA = 0.12
    SEGURO = 0.04
    OTROS_DESCUENTOS = 0.03
    VALOR_HORA_EXTRA = 25.0

    def __init__(self, empleado_id: int, salario_base: float, horas_extra: float = 0.0):
        self.empleado_id = empleado_id
        self.salario_base = salario_base
        self.horas_extra = horas_extra

    def calcular_total_extra(self) -> float:
        return self.horas_extra * self.VALOR_HORA_EXTRA

    def calcular_descuentos(self) -> float:
        return self.salario_base * (self.IVA + self.SEGURO + self.OTROS_DESCUENTOS)

    def calcular_neto(self) -> float:
        total_extra = self.calcular_total_extra()
        descuentos = self.calcular_descuentos()
        return round(self.salario_base + total_extra - descuentos, 2)

    def resumen(self) -> Dict[str, float]:
        total_extra = self.calcular_total_extra()
        descuentos = self.calcular_descuentos()
        return {
            "salario_base": self.salario_base,
            "total_extra": total_extra,
            "descuentos": round(descuentos, 2),
            "neto": self.calcular_neto(),
        }
