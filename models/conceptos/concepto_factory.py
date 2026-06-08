from typing import Optional
from .concepto_fijo import ConceptoFijo
from .concepto_variable import ConceptoVariable
from .concepto_porcentaje import ConceptoPorcentaje


class ConceptoFactory:
    @staticmethod
    def crear(tipo: str, nombre: str, valor: Optional[float] = None, porcentaje: Optional[float] = None, base_calculo: Optional[str] = None):
        t = tipo.lower() if isinstance(tipo, str) else ""
        if t == "fijo":
            return ConceptoFijo(nombre=nombre, valor=float(valor or 0.0))
        if t == "variable":
            return ConceptoVariable(nombre=nombre)
        if t == "porcentaje":
            return ConceptoPorcentaje(nombre=nombre, porcentaje=float(porcentaje or 0.0), base_calculo=base_calculo or "salario")
        raise ValueError(f"Tipo de concepto desconocido: {tipo}")
