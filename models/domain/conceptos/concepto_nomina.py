"""
Modelo de dominio ConceptoNomina.
Solo datos y validaciones básicas. Sin lógica de negocio ni persistencia.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class ConceptoNomina:
    """Plantilla de concepto de nómina (catálogo)"""
    id: Optional[int] = None
    nombre: str = ""
    tipo: str = "fijo"  # fijo, variable, porcentaje
    valor: Optional[float] = None
    porcentaje: Optional[float] = None
    base_calculo: Optional[str] = "salario"  # salario, ventas, etc.
    naturaleza: str = "devengado"  # devengado o deduccion
    activo: bool = True
    
    def validar(self) -> tuple[bool, str]:
        """Validación básica de datos"""
        if not self.nombre:
            return False, "Nombre es obligatorio"
        if self.tipo not in ["fijo", "variable", "porcentaje"]:
            return False, "Tipo debe ser fijo, variable o porcentaje"
        if self.tipo == "fijo" and self.valor is None:
            return False, "Concepto fijo requiere valor"
        if self.tipo == "porcentaje" and self.porcentaje is None:
            return False, "Concepto porcentaje requiere porcentaje"
        if self.naturaleza not in ["devengado", "deduccion"]:
            return False, "Naturaleza debe ser devengado o deduccion"
        return True, ""
    
    def to_dict(self) -> Dict[str, object]:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "tipo": self.tipo,
            "valor": self.valor,
            "porcentaje": self.porcentaje,
            "base_calculo": self.base_calculo,
            "naturaleza": self.naturaleza,
            "activo": self.activo,
        }
